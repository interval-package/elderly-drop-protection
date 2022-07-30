# -*-coding:utf-8-*-

import threading
import os
import sys
import json
import random
import time
import paho.mqtt.client as mqtt
import math
from IoT_device.utils import get_password, get_client_id
from IoT_device.utils import get_request_id_from_msg, get_device_id_from_msg
from IoT_device.request import Command, DeviceMessage

# 当前文件的祖父目录
GRAND_PATH = os.path.abspath(os.path.dirname(__file__) + os.path.sep + '..')

retryTimes = 0

class IotClient(threading.Thread):
    def __init__(self, client_cfg):
        """
        client_cfg：客户信息，包括以下内容：
        server_ip:  IoT平台mqtt对接地址
        device_id:  创建设备时获得的deviceId，
        secret:  创建设备时获得的密钥
        is_ssl: True则建立 ssl 连接
        ssl_certification_path: # ssl证书存放路径
        """
        super(IotClient, self).__init__()
        self.__server_ip = client_cfg.server_ip
        self.__device_id = client_cfg.device_id
        self.__secret = client_cfg.secret
        self.__is_ssl = client_cfg.is_ssl
        self.__port = 1883
        self.__ssl_certification_path = GRAND_PATH + r'/resources/DigiCertGlobalRootCA.crt.pem'
        self.__client = mqtt.Client(client_id=get_client_id(self.__device_id))
        self.__set_callback()
        self.__command_callback = None
        self.__device_message_callback = None
        self.__property_set_callback = None
        self.__property_get_callback = None
        self.__user_topic_message_callback = None
        self.__publish_result = mqtt.MQTT_ERR_SUCCESS
        self.__subscribe_result = mqtt.MQTT_ERR_SUCCESS
        self.__user_defined_topic = list()

    # 启动线程
    def run(self):
        self.__client.loop_forever()  # 在无限阻塞循环中调用loop（）,进入循环监听

    # 设置回调函数
    def __set_callback(self):
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message_received
        self.__client.on_subscribe = self.__on_subscribe
        self.__client.on_publish = self.__on_publish
        self.__client.on_log = self.__on_log

    # 建立mqtt连接
    def connect(self):
        print("......Mqtt/Mqtts connecting......")
        if self.__is_ssl:
            self.__mqtt_with_ssl_connect_config()
        else:
            self.__mqtt_connect_config()
        # 设置用户名，密码
        self.__client.username_pw_set(self.__device_id, get_password(self.__secret))
        # 连接至broker
        self.__client.connect(host=self.__server_ip, port=self.__port, keepalive=60)

        print("-----------------Mqtt/Mqtts connection completed !!!")

    # mqtt连接端口设置
    def __mqtt_connect_config(self):
        print('congfigure mqtt connect port')
        self.__port = 1883

    # mqtts连接证书，端口设置
    def __mqtt_with_ssl_connect_config(self):
        print('congfigure mqtt with ssl connect')
        if not os.path.isfile(self.__ssl_certification_path):
            raise ValueError('ssl certification path error')
        self.__client.tls_set(ca_certs=self.__ssl_certification_path)  # ca_certs 为证书存放路径
        self.__client.tls_insecure_set(True)  # 设置为True表示不用验证主机名
        self.__port = 8883

    # 订阅topic
    def __subscribe(self):
        # 订阅平台下发命令topic
        self.__subscribe_result, _ = self.__client.subscribe(
            r'$oc/devices/' + str(self.__device_id) + r'/sys/commands/#', qos=1)
        # 订阅平台消息下发topic
        self.__subscribe_result, _ = self.__client.subscribe(
            r'$oc/devices/' + str(self.__device_id) + r'/sys/messages/down', qos=1)
        # 订阅平台设置设备属性topic
        self.__subscribe_result, _ = self.__client.subscribe(
            r'$oc/devices/' + str(self.__device_id) + r'/sys/properties/set/#', qos=1)
        # 订阅平台查询设备属性topic
        self.__subscribe_result, _ = self.__client.subscribe(
            r'$oc/devices/' + str(self.__device_id) + "/sys/properties/get/#", qos=1)
        # 订阅设备侧主动获取平台设备影子数据的响应topic
        self.__subscribe_result, _ = self.__client.subscribe(
            r'$oc/devices/' + str(self.__device_id) + r'/sys/shadow/get/response/#', qos=1)

    # 订阅topic
    def subscribe(self, topic):
        print("......Subscription topic......")
        if isinstance(topic, str):
            self.__single_subscribe(topic)
        elif isinstance(topic, list):
            self.__batch_subscribe(topic)

    # 批量订阅topic
    def __batch_subscribe(self, topic_list):
        for topic in topic_list:
            self.__single_subscribe(topic)

    # 订阅单个topic
    def __single_subscribe(self, topic):
        self.__subscribe_result, _ = self.__client.subscribe(topic, qos=1)
        if self.__subscribe_result == mqtt.MQTT_ERR_SUCCESS:
            self.__user_defined_topic.append(topic)
            print("------You have subscribed: ", topic)
        else:
            print('Subscription failed: ', topic)

    # 解除订阅topic
    def unsubscribe(self, topic):
        print("......Unsubscription topic......")
        if isinstance(topic, str):
            self.__single_unsubscribe(topic)
        elif isinstance(topic, list):
            self.__batch_unsubscribe(topic)

    # 批量解除订阅topic
    def __batch_unsubscribe(self, topic_list):
        for topic in topic_list:
            self.__single_unsubscribe(topic)

    # 单个解除订阅topic
    def __single_unsubscribe(self, topic):
        result, _ = self.__client.unsubscribe(topic)
        if result == mqtt.MQTT_ERR_SUCCESS:
            print("------You have unsubscribed:", topic)
        else:
            print('Unsubscription failed: ', topic)

    # 设置回调，根据topic判断，平台操作的类型
    def __on_message_received(self, client, userdata, msg):
        print("\n====== The message is received from the platform ====== \n", "Topic: " + msg.topic,
              "\npayload: " + msg.payload.decode("utf-8"))
        if r'/sys/commands/request_id' in msg.topic:
            self.__on_command(msg)  # 设备响应平台命令下发
        elif r'/sys/messages/down' in msg.topic:
            self.__on_device_message(msg)  # 设备响应平台消息下发
        elif r'/sys/properties/set/request_id' in msg.topic:
            print('--------------type(msg)', type(msg), '------')
            self.__on_property_set(msg)  # 设备响应平台设置设备属性
        elif '/sys/properties/get/request_id' in msg.topic:
            self.__on_property_get(msg)  # 设备响应平台查询设备属性
        else:
            self.__on_other(msg)

    def report_properties(self, service_properties, qos):
        '''
        设备上报属性:上报json数据，注意serviceId要与Profile中的定义对应
        :param service_properties:服务与属性，参考ServicesProperties类
        :param qos:消息质量等级
        :return:无
        '''
        print("......Device reporting properties......")
        topic = r'$oc/devices/' + str(self.__device_id) + r'/sys/properties/report'
        payload = {"services": service_properties}
        payload = json.dumps(payload)
        self.__client.publish(topic, payload, qos=qos)
        print("-----------------Device report properties completed-----------------")

    # 设备发送消息到平台,又用户自定义topic
    def __publish_raw_message(self, topic, device_message):
        payload = {"content": device_message}
        payload = json.dumps(payload)
        self.__publish_result, _ = self.__client.publish(topic, payload, qos=1)

    # 设备发送消息到平台,
    def publish_message(self, *args):
        if len(args) == 1:  # 系统定义topic
            (device_message,) = args
            topic = '$oc/devices/' + str(self.__device_id) + r'/sys/messages/up'
            self.__publish_raw_message(topic, device_message)
        elif len(args) == 2:  # 用户自定义topic
            topic, device_message = args
            self.__publish_raw_message(topic, device_message)

    # 响应平台下发的命令
    def respond_command(self, request_id, result_code):
        topic = r'$oc/devices/' + str(self.__device_id) + r'/sys/commands/response/request_id=' + request_id
        payload = {"result_code": result_code}
        payload = json.dumps(payload)
        self.__client.publish(topic, payload, qos=1)

    # 响应平台下发的命令
    def respond_device_message(self, message):
        print("------The platform has sent a message------", message)
        print("------ message topic", message.topic)
        print("------message payload", message.payload)

    # 响应平台设置设备属性
    def respond_property_set(self, request_id, result_code):
        topic = r'$oc/devices/' + str(self.__device_id) + r'/sys/properties/set/response/request_id=' + request_id
        payload = {"result_code": 0, "result_desc": result_code}
        payload = json.dumps(payload)
        self.__client.publish(topic, payload, qos=1)

    # 响应平台查询设备属性
    def respond_property_get(self, request_id, service_properties):
        topic = r'$oc/devices/' + str(self.__device_id) + r'/sys/properties/get/response/request_id=' + request_id
        payload = {"services": service_properties}
        payload = json.dumps(payload)
        self.__client.publish(topic, payload, qos=1)

    # 平台下发命令后，设备发送响应
    def __on_command(self, command):
        print("-----------------Response command-----------------")
        request_id = get_request_id_from_msg(command)  # 得到request_id
        comm = Command(json.loads(command.payload))
        if self.__command_callback != None and (
                get_device_id_from_msg(command) == None or get_device_id_from_msg(command) == self.__device_id):
            self.__command_callback(request_id, comm)
        else:
            self.respond_command(request_id, result_code=0)

    # 响应平台下发消息
    def __on_device_message(self, msg):
        device_message = DeviceMessage(json.loads(msg.payload))
        if self.__device_message_callback != None and (
                get_device_id_from_msg(msg) == None or get_device_id_from_msg(msg) == self.__device_id):
            self.__device_message_callback(device_message)
        else:
            self.respond_device_message(msg)

    # 响应设置设备属性
    def __on_property_set(self, msg):
        print("-----------------Response platform setting device properties-----------------")
        request_id = get_request_id_from_msg(msg)  # 得到request_id
        if self.__property_set_callback != None and (
                get_device_id_from_msg(msg) == None or get_device_id_from_msg(msg) == self.__device_id):
            self.__property_set_callback(request_id, msg.payload)
        else:
            self.respond_property_set(request_id, result_code="success")

    # 响应设置
    def __on_property_get(self, msg):
        print("-----------------Response platform query device properties-----------------")
        request_id = get_request_id_from_msg(msg)  # 得到request_id
        if self.__property_get_callback != None and (
                get_device_id_from_msg(msg) == None or get_device_id_from_msg(msg) == self.__device_id):
            self.__property_get_callback(request_id, msg.payload)
        else:
            service_id = json.loads(msg.payload)['service_id']
            self.respond_property_get(request_id, [{'service_id': service_id}])

    # 处理自定义
    def __on_other(self, msg):
        device_message = DeviceMessage(json.loads(msg.payload))
        if msg.topic in self.__user_defined_topic:
            if self.__user_topic_message_callback != None and (
                    get_device_id_from_msg(msg) == None or get_device_id_from_msg(msg) == self.__device_id):
                self.__user_topic_message_callback(device_message)
            else:
                self.respond_device_message(msg)
        else:
            print("-----------------This topic is not subscribed-----------------")

    # 设置连接的回调
    def __on_connect(self, client, userdata, flags, rc):
        global retryTimes
        if rc == 0:
            retryTimes = 0
            print("-----------------Connection successful !!!")
            self.__subscribe()  # 订阅系统定义topic
        else:
            print("-----------------Connection fail !!!,\n", "Connected with result code " + str(rc))
            self.retreat_reconnection()

    # 退避重连
    def retreat_reconnection(self):
        print("---- 退避重连")

        global retryTimes
        minBackoff = 1
        maxBackoff = 30
        defaultBackoff = 1

        low_bound = (int)(defaultBackoff * 0.8)
        high_bound = (int)(defaultBackoff * 1.2)
        random_backoff = random.randint(0, high_bound - low_bound)
        backoff_with_jitter = math.pow(2.0, retryTimes) * (random_backoff + low_bound)
        wait_time_until_next_retry = min(minBackoff + backoff_with_jitter, maxBackoff)
        print("the next retry time is ", wait_time_until_next_retry, " seconds")
        retryTimes += 1
        time.sleep(wait_time_until_next_retry)
        self.connect()

    # 设置订阅消息的回调
    def __on_subscribe(self, client, userdata, mid, granted_qos):
        print("---Subscribe mid = " + str(mid))

    # 设置已发布的消息的回调
    def __on_publish(self, client, userdata, mid):
        if self.__publish_result == mqtt.MQTT_ERR_SUCCESS:
            print("Publish success---mid = " + str(mid))
        else:
            print("Publish fail---mid = " + str(mid))

    # 设置日志记录的回调
    def __on_log(self, client, userdata, level, buf):
        print("Log:" + buf)  # 打印日志

    # 用户自定义回调
    def set_command_callback(self, callback):
        self.__command_callback = callback

    def set_device_message_callback(self, callback):
        self.__device_message_callback = callback

    def set_property_set_callback(self, callback):
        self.__property_set_callback = callback

    def set_property_get_callback(self, callback):
        self.__property_get_callback = callback

    def set_user_topic_message_callback(self, callback):
        self.__user_topic_message_callback = callback



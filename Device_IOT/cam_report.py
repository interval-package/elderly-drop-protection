# -*- encoding: utf-8 -*-
'''
平台下发命令 demo
'''
import json
import logging

from Device_IOT.IoT_device.request import ServicesProperties
from IoT_device.client.IoT_client_config import IoTClientConfig
from IoT_device.client.IoT_client import IotClient

# 日志设置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class cam_report(object):

    def __init__(self, client_cfg=None):
        # 客户端配置
        if client_cfg is None:
            self.client_cfg = IoTClientConfig(server_ip='iot-mqtts.cn-north-4.myhuaweicloud.com',
                                         device_id='5e85a55f60b7b804c51ce15c_py123',
                                         secret='123456789', is_ssl=True)
        else:
            self.client_cfg = client_cfg
        # 创建设备
        self.iot_client = IotClient(self.client_cfg)

        # 自定义callback

    def property_set_callback(self, request_id, payload):
        # 遍历services
        for service in json.loads(payload)['services']:
            logger.info(('property set service id = ', service['service_id']))
            for property in service['properties']:
                logger.info(('property name = ', property))
                logger.info(('property value = ', service['properties'][property]))

        # 上行响应
        self.iot_client.respond_property_set(request_id, result_code='success')
        # 上报属性
        service_property = ServicesProperties()
        service_property.add_service_property(service_id="Battery", property='batteryLevel', value=1)
        self.iot_client.report_properties(service_property.service_property, qos=1)
        print('------------------this is myself callback')

        # 自定义callback

    def property_get_callback(self, request_id, payload):
        logger.info(('property get service id:', json.loads(payload)['service_id']))
        service_property = ServicesProperties()
        service_property.add_service_property(service_id="Battery", property='batteryLevel', value=2)
        service_property.add_service_property(service_id="analog", property='PHV-phsA', value=1)
        self.iot_client.respond_property_get(request_id, service_property.service_property)
        print('------------------this is myself callback')

    # 响应平台下发命令
    def command_callback(self, request_id, command):
        logger.info(('Command, device id:  ', command.device_id))
        logger.info(('Command, service id = ', command.service_id))
        logger.info(('Command, command name: ', command.command_name))
        logger.info(('Command. paras: ', command.paras))
        # result_code:设置为零相应命令下发成功，为 1 下发命令失败
        self.iot_client.respond_command(request_id, result_code=0)
        print('------------------this is myself callback')

    def run_default(self):
        self.iot_client.connect()  # 建立连接

        # 设置响应命令的回调
        self.iot_client.set_command_callback(
            self.command_callback)

        self.iot_client.start()  # 线程启动

    def set_message_property(self):
        """
        订阅自定义topic, 需提前在平台配置自定义topic
        支持批量订阅（topic存放列表中），和逐个订阅（单个topic,无需放入列表）
        """
        topic_1 = r'$oc/devices/' + str(self.client_cfg.device_id) + r'/user/user_message/up'
        topic_2 = r'$oc/devices/' + str(self.client_cfg.device_id) + r'/user/myself_prop/up'
        topic_3 = r'$oc/devices/' + str(self.client_cfg.device_id) + r'/user/wpy/up'
        self.iot_client.subscribe(topic=[topic_1, topic_2, topic_3])
        # 取消订阅，使用方法同订阅功能
        self.iot_client.unsubscribe(topic_1)

    def send_message(self):

        # 发送自定义topic消息
        self.iot_client.publish_message(r'$oc/devices/' + str(self.client_cfg.device_id) + r'/user/wpy/up',
                                   'Hello Huawei cloud IoT')

        # 设备向平台发送消息，系统默认topic
        self.iot_client.publish_message('raw message: Hello Huawei cloud IoT')


if __name__ == '__main__':
    obj = cam_report()
    obj.run_default()

# -*- encoding: utf-8 -*-
'''
消息传送demo
包括订阅topic
发布消息
'''

import logging

from IoT_device.client import IoTClientConfig
from IoT_device.client import IotClient


# 日志设置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    # 客户端配置
    client_cfg = IoTClientConfig(server_ip='iot-mqtts.cn-north-4.myhuaweicloud.com',
                                 device_id='5e85a55f60b7b804c51ce15c_py123',
                                 secret='123456789', is_ssl=False)
    # 创建设备
    iot_client = IotClient(client_cfg)
    iot_client.connect()  # 建立连接

    # 设备接受平台下发消息的响应
    def message_callback(device_message):
        logger.info(('device message, device id:  ', device_message.device_id))
        logger.info(('device message, id = ', device_message.id))
        logger.info(('device message, name: ', device_message.name))
        logger.info(('device message. content: ', device_message.content))
    # 设置平台下发消息响应的回调
    iot_client.set_device_message_callback(message_callback)
    # 设置平台下发自定义topic消息响应的回调
    iot_client.set_user_topic_message_callback(message_callback)

    '''
    订阅自定义topic, 需提前在平台配置自定义topic
    支持批量订阅（topic存放列表中），和逐个订阅（单个topic,无需放入列表）
    '''
    topic_1 = r'$oc/devices/' + str(client_cfg.device_id) + r'/user/user_message/up'
    topic_2 = r'$oc/devices/' + str(client_cfg.device_id) + r'/user/myself_prop/up'
    topic_3 = r'$oc/devices/' + str(client_cfg.device_id) + r'/user/wpy/up'
    iot_client.subscribe(topic=[topic_1, topic_2, topic_3])
    # 取消订阅，使用方法同订阅功能
    iot_client.unsubscribe(topic_1)

    # 发送自定义topic消息
    iot_client.publish_message(r'$oc/devices/' + str(client_cfg.device_id) + r'/user/wpy/up', 'Hello Huawei cloud IoT')

    # 设备向平台发送消息，系统默认topic
    iot_client.publish_message('raw message: Hello Huawei cloud IoT')

    iot_client.start()  # 线程启动

if __name__ == '__main__':
    run()

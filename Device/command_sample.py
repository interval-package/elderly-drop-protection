# -*- encoding: utf-8 -*-
'''
平台下发命令 demo
'''

import logging

from IoT_device.client.IoT_client_config import IoTClientConfig
from IoT_device.client.IoT_client import IotClient


# 日志设置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    # 客户端配置
    client_cfg = IoTClientConfig(server_ip='iot-mqtts.cn-north-4.myhuaweicloud.com',
                                 device_id='5e85a55f60b7b804c51ce15c_py123',
                                 secret='123456789', is_ssl=True)
    # 创建设备
    iot_client = IotClient(client_cfg)
    iot_client.connect()  # 建立连接

    # 响应平台下发命令
    def command_callback(request_id, command):
        logger.info(('Command, device id:  ', command.device_id))
        logger.info(('Command, service id = ', command.service_id))
        logger.info(('Command, command name: ', command.command_name))
        logger.info(('Command. paras: ', command.paras))
        # result_code:设置为零相应命令下发成功，为 1 下发命令失败
        iot_client.respond_command(request_id, result_code=0)
        print('------------------this is myself callback')
    # 设置响应命令的回调
    iot_client.set_command_callback(command_callback)

    iot_client.start()  # 线程启动

if __name__ == '__main__':
    run()

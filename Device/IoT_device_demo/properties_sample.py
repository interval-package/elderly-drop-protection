# -*- encoding: utf-8 -*-
'''
平台设置属性，查询属性，设备上报属性demo
'''
import time
import logging
import json

from IoT_device.client.IoT_client_config import IoTClientConfig
from IoT_device.client.IoT_client import IotClient
from IoT_device.request.services_properties import ServicesProperties

# 日志设置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    # 客户端配置
    client_cfg = IoTClientConfig(server_ip='iot-mqtts.cn-north-4.myhuaweicloud.com',
                                 device_id='5ebac693352cfb02c567ec88_abcdefg1234',
                                 secret='yourSecret', is_ssl=True)

    # 创建设备
    iot_client = IotClient(client_cfg)
    iot_client.connect() # 建立连接

    # 自定义callback
    def property_set_callback(request_id, payload):
        # 遍历services
        for service in json.loads(payload)['services']:
            logger.info(('property set service id = ', service['service_id']))
            for property in service['properties']:
                logger.info(('property name = ', property))
                logger.info(('property value = ', service['properties'][property]))

        # 上行响应
        iot_client.respond_property_set(request_id, result_code='success')
        # 上报属性
        service_property = ServicesProperties()
        service_property.add_service_property(service_id="Battery", property='batteryLevel', value=1)
        iot_client.report_properties(service_property.service_property, qos=1)
        print('------------------this is myself callback')

    # 自定义callback
    def property_get_callback(request_id, payload):
        logger.info(('property get service id:', json.loads(payload)['service_id']))
        service_property = ServicesProperties()
        service_property.add_service_property(service_id="Battery", property='batteryLevel', value=2)
        service_property.add_service_property(service_id="analog", property='PHV-phsA', value=1)
        iot_client.respond_property_get(request_id, service_property.service_property)
        print('------------------this is myself callback')

    # 设置平台设置设备属性的回调
    iot_client.set_property_set_callback(property_set_callback)
    # 设置平台查询设备属性的回调
    iot_client.set_property_get_callback(property_get_callback)
    iot_client.start()  # 线程启动

    # 定时上报属性
    while True:
        # 按照产品模型设置属性
        service_property = ServicesProperties()
        service_property.add_service_property(service_id="Battery", property='batteryLevel', value=1)
        service_property.add_service_property(service_id="Battery", property='batteryThreshold', value=2)
        service_property.add_service_property(service_id="Connectivity", property='rsrp', value=3)
        service_property.add_service_property(service_id="Connectivity", property='cellId', value=4)
        service_property.add_service_property(service_id="WaterMeter", property='temperature', value=90)
        iot_client.report_properties(service_properties=service_property.service_property, qos=1)
        time.sleep(10)

if __name__ == '__main__':
    run()

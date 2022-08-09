from IoT_device.client.IoT_client_config import IoTClientConfig
from IoT_device.client.IoT_client import IotClient
from IoT_device.request.services_properties import ServicesProperties


# 这个脚本这里直接进行连接

client_cfg = IoTClientConfig(server_ip='iot-mqtts.cn-north-4.myhuaweicloud.com',
                             device_id='5e85a55f60b7b804c51ce15c_py123',
                             secret='123456789', is_ssl=True)

server_ip = "fcd87681b6.iot-mqtts.cn-north-4.myhuaweicloud.com"

# 创建设备
iot_client = IotClient(client_cfg)
iot_client.connect()  # 建立连接


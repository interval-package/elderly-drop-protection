# -*- encoding: utf-8 -*-

from IoT_device.utils.IoT_util import str_is_empty


class IoTClientConfig:
    def __init__(self, server_ip='', device_id='', secret='', is_ssl=False):
        '''
        配置客户端相关信息
        serverIp: IoT平台mqtt对接地址
        device_id: 创建设备时获得的deviceId
        secret: 创建设备时设置的密钥（要替换为自己注册的设备ID与密钥）
        is_ssl: 必须为bool类型，若为 True 则建立MQTTS连接，加载服务器端SSL证书，,否则建立MQTT连接
        '''
        self.__server_ip = server_ip
        self.__device_id = device_id
        self.__secret = secret
        self.__is_ssl = is_ssl

    @property
    def server_ip(self):
        if self.__server_ip == '':
            raise ValueError('You have not set the server_ip')
        return self.__server_ip

    @server_ip.setter
    def server_ip(self, value):
        if str_is_empty(value):
            raise ValueError('server_ip Wrong !!!, the server_ip is empty')
        self.__server_ip = value

    @property
    def device_id(self):
        if self.__device_id == '':
            raise ValueError('You have not set the device_id')
        return self.__device_id

    @device_id.setter
    def device_id(self, value):
        if str_is_empty(value):
            raise ValueError('device_id Wrong !!!, the device_id is empty')
        self.__device_id = value

    @property
    def secret(self):
        if self.__secret == '':
            raise ValueError('You have not set the secret')
        return self.__secret

    @secret.setter
    def secret(self, value):
        if str_is_empty(value):
            raise ValueError('secret Wrong !!!, the secret is empty')
        self.__secret = value

    @property
    def is_ssl(self):
        return self.__is_ssl

    @is_ssl.setter
    def is_ssl(self, value):
        if isinstance(value, bool):
            raise ValueError('Invalid is_ssl !!!, is_ssl should be an instance of type bool')
        self.__is_ssl = value

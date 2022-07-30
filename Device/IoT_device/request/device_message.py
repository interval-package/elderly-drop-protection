# -*- encoding: utf-8 -*-
'''设备消息
'''

class DeviceMessage:
    def __init__(self, message=dict()):
        self.__object_device_id = None
        self.__id = None
        self.__name = None
        self.__content = None
        self.__message = message
        self.__set_message()

    def __set_message(self):
        if 'object_device_id' in self.__message.keys():
            self.__object_device_id = self.__message['object_device_id']
        if 'id' in self.__message.keys():
            self.__id = self.__message['id']
        if 'name' in self.__message.keys():
            self.__name = self.__message['name']
        if 'content' in self.__message.keys():
            self.__content = self.__message['content']

    @property
    def device_id(self):
        return self.__object_device_id

    @device_id.setter
    def device_id(self, value):
        self.__object_device_id = value

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, value):
        self.__content = value

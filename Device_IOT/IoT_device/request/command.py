# -*- encoding: utf-8 -*-
'''设备命令
'''
class Command:
    def __init__(self, command_dict):
        self.__object_device_id = None
        self.__service_id = None
        self.__command_name = None
        self.__paras = None
        self.__command = command_dict
        self.__set_command()

    def __set_command(self):
        if 'object_device_id' in self.__command.keys():
            self.__object_device_id = self.__command['object_device_id']
        if 'command_name' in self.__command.keys():
            self.__command_name = self.__command['command_name']
        if 'service_id' in self.__command.keys():
            self.__service_id = self.__command['service_id']
        if 'paras' in self.__command.keys():
            self.__paras = self.__command['paras']

    @property
    def service_id(self):
        return self.__service_id

    @property
    def device_id(self):
        return self.__object_device_id

    @property
    def command_name(self):
        return self.__command_name

    @property
    def paras(self):
        return self.__paras

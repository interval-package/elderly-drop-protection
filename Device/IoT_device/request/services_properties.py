# -*- encoding: utf-8 -*-
'''
定义服务的属性
'''

class ServicesProperties:
    def __init__(self):
        self.__services_properties = list()


    def add_service_property(self, service_id, property, value):
        service_property_dict = {"service_id": service_id, "properties": {property: value}}
        self.__services_properties.append(service_property_dict)


    @property
    def service_property(self):
        return self.__services_properties


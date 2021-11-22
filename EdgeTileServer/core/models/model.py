#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, November 27th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from abc import abstractmethod

class Model:
    def __init__(self, component, component_name):
        super().__init__()
        self.component = component
        self.component_name = component_name
        self.logger = component.logger.getChild(component_name)
        self.config = component.config[component_name]
        self.__is_initialized = False
    
    def init(self):
        self._initialize()
        self.__is_initialized = True

    @abstractmethod
    def _initialize(self):
        pass
    
    @abstractmethod
    def detect(self, frame):
        pass

    
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Tuesday, November 26th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from abc import abstractmethod
from utils.stoppable_thread import StoppableThread

class EdgeComponent(StoppableThread):
    def __init__(self, app, component_name):
        super().__init__()
        self.app = app
        self.component_name = component_name
        self.logger = app.logger.getChild(component_name)
        config_urls = component_name.split('/')
        self.config = app.config[app.app_name]
        for url in config_urls:
            self.config = self.config[url]
        self.__is_initialized = False
    
    def init(self):
        self._initialize()
        self.__is_initialized = True
    
    def is_init(self):
        return self.__is_initialized

    @abstractmethod
    def _initialize(self):
        pass

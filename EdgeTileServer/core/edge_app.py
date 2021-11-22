#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Tuesday, November 26th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from utils.custom_logging import get_logger
from config.load_config import load_config
from abc import abstractmethod

class EdgeApp:
    def __init__(self, app_name, logger_name):
        super().__init__()
        self.app_name = app_name
        self.logger = get_logger(logger_name)
        self.config = load_config(self.logger)
        self.components = dict()

    def register(self, component_name, component_class):
        component = component_class(self)
        setattr(self, component_name, component)
        self.components[component_name] = getattr(self, component_name)
        self.logger.info(f"register component {component_name} success")
    
    def initialize(self):
        for k, v in self.components.items():
            v.init()
            self.logger.info(f"component {k} initialize success")

    def start_components(self):
        for k, v in self.components.items():
            v.start()
            self.logger.info(f"component {k} start success")

    def join(self):
        for _, v in self.components.items():
            v.join()

    def stop(self):
        self.logger.info("stop app")
        for _, v in self.components.items():
            v.stop()

    @abstractmethod
    def start(self):
        pass
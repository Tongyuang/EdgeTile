#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, November 30th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from abc import abstractmethod
from collections import OrderedDict

class LogParser:
    def __init__(self):
        super().__init__()
        self.key_idx = None
        self.__val = OrderedDict()

    @abstractmethod
    def parse(self, dict_data):
        pass
    
    @abstractmethod
    def prepare_dump():
        pass

    def dump(self):
        self.prepare_dump()
        return self.__val

    @abstractmethod
    def load(self):
        pass

    def set_attr(self, attr_name, attr_val):
        self.__val[attr_name] = attr_val

    def get_attr(self, attr_name):
        return self.__val[attr_name]
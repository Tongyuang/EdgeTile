#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, November 21st 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import yaml
import re

def load_config(logger=None):
    try:
        yaml_file = 'config/config.yaml'
        f = open(yaml_file, 'r', encoding='utf-8')
        config = yaml.load(f.read(), Loader=yaml.SafeLoader)
        f.close()
        if logger:
            logger.info("load config file success")
    except:
        if logger:
            logger.error("load config file error")
        return None
    return config

def load_class_name():
    f = open('data/yolov3_class.names', 'r')
    class_name_map = dict()
    for l in f.readlines():
        x = re.findall("(\w+) \d+ (\w+)", l)
        if len(x) == 1:
            class_name_map[x[0][0]] = x[0][1]
    return class_name_map

global_config = load_config(None)
# global_class_name_map = load_class_name()

if __name__ == "__main__":
    load_class_name()   
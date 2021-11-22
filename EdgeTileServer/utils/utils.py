#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, November 18th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import time
import datetime

def get_ms_time():
    return time.time() * 1000.0

def get_second_time():
    return time.time()

def sleep_ms_time(ms_time):
    time.sleep(ms_time / 1000.0)

def mstimestamp_to_str(ms_timestamp):
    return datetime.datetime.fromtimestamp(ms_timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def str_to_mstimestamp(s):
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
    return d.timestamp() * 1000


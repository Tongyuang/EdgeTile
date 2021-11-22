#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, November 30th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import logging

def get_logger(logger_name):
    # init logging
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    log_file = "data/log/" + logger_name + ".log"
    file_hdl_log = logging.FileHandler(log_file, mode='w+')
    file_hdl_log.setLevel(logging.DEBUG)
    file_hdl_log.setFormatter(formatter)
    logger.addHandler(file_hdl_log)
    logger.info("Start logging...")
    return logger
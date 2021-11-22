#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Sunday, July 19th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
import os
path = '/Users/wangxu/jpeg/jpg'
for filename in os.listdir(path):
    prefix, num = filename[:-4].split('_')
    num = num.zfill(4)
    new_filename = prefix + "_" + num + ".jpg"
    os.rename(os.path.join(path, filename), os.path.join(path, new_filename))
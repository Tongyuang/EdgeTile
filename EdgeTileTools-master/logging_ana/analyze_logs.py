#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, May 27th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
import pathlib


exp_name = '4group_dynamic3'
root_path = '/Users/wangxu/Edge/EdgeTileClient/data/drone/track'
file_path = pathlib.Path(root_path) / exp_name / 'uav0000137_00458_v.yaml'
data = yaml.load(open(file_path, 'r'))
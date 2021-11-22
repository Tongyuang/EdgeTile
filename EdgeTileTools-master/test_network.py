#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, July 13th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
import numpy as np
ip = "166.111.80.127"
port = 10051

import socket 
s = socket.socket()   
host = socket.gethostname() # 获取本地主机名
s.connect((ip, port))
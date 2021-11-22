#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, February 22nd 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
#!/usr/bin/env python

import socket


TCP_IP = '166.111.80.127'
TCP_PORT = 10051
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"
file_name = "bluefox_2016-10-26-12-49-56_bag.mp4_0.hevc"
f = open('../../EdgeTileClient/data/hevc/' + file_name, 'rb')
buffer = f.read()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
len_count = len(buffer)
s.send(bytes([len_count]))

print(len(buffer))
l = 0
while l < len(buffer):
    t = s.send(buffer[l:])
    l = l + t
s.close()

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


TCP_IP = '0.0.0.0'
TCP_PORT = 10051
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
f = open("a.hevc", "wb")
print('Connection address:', addr)

size = conn.recv(4)
size = int.from_bytes(size)
print(size)
l = 0
while l < size:
    data = conn.recv(BUFFER_SIZE)
    if data:
        f.write(data)
    l += len(data)

f.close()
conn.close()

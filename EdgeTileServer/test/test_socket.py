#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, February 22nd 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from utils.json_socket import JsonSocket, SocketType
from utils.custom_logging import get_logger
import sys 
import time

def client():
    s = JsonSocket("166.111.80.127", 10050, SocketType.CLIENT_MODE, get_logger("client"))
    s.start()
    t1 = time.time()
    s.send(open("/Users/wangxu/Git/EdgeTile-Client/data/drone/anno/uav0000137_00458_v/000001.xml", "r").read())
    t2 = time.time()
    print(t2 - t1)
def server():
    s = JsonSocket("166.111.80.127", 10050, SocketType.SERVER_MODE, get_logger("server"))
    # s.send(open("/Users/wangxu/Git/EdgeTile-Client/data/drone/anno/uav0000073_04464_v/000001.xml", "r").read())
    s.start()
    t1 = time.time()
    msg = s.recv()
    t2 = time.time()

    print(msg)
    print(t2 - t1)

if __name__== "__main__":
    if sys.argv[1] == "0":
        print("client")
        client()
    else:
        print("server")
        server()
    

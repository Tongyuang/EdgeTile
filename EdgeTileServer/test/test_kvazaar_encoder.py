#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, November 18th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''

import sys
sys.path.insert(0, "dist/python3")
import cv2
import time
import numpy as np
def encode_callback(tid, len, data):
    print(tid)

def test_kvazaar_encoder():
    width = 1280
    height = 720
    yuv_file = "data/ILSVRC_sample/video/ILSVRC2015_val_00000000.yuv"
    f = open(yuv_file, 'rb')

    encoder = cv2.kvazaar_encoder_KvazaarEncoder("ILSVRC2015_val_00000000")
    # encoder.setServerMode("127.0.0.1", 8080)
    encoder.setFileMode("video1")
    encoder.start(width, height, 8, '3x3', 16, 'superfast')
    i = 0
    start = time.time()
    while True:
        y = f.read(width * height)
        u = f.read(int(width * height / 4))
        v = f.read(int(width * height / 4))
        y = np.frombuffer(y, dtype=np.uint8)
        u = np.frombuffer(u, dtype=np.uint8)
        v = np.frombuffer(v, dtype=np.uint8)
        if len(y) > 0:
            while True:
                res = encoder.encode(y, u, v, i)
                if res.encoderState == 0:
                    time.sleep(0.005)
                    continue
                else:
                    end = time.time()
                    print(f"frame rate: {i / (end - start)}")
                    break
            i += 1
            
            # print("come here")
        else:
            encoder.stop()
            break
    while encoder.getEncodeStatus() >= 0:
        continue
    print("finish")

if __name__ == '__main__':
    test_kvazaar_encoder()
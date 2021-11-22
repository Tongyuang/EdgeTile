#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, November 20th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import sys
sys.path.insert(0, "dist/python3")
import cv2
import time
import numpy as np

def test_openhevc_decoder():
    decoder = cv2.openhevc_decoder_OpenHEVCDecoder()
    print("here")
    decoder.start(8080)
    while(1):
        f = decoder.read()
        if f.frame_id < 0:
            break
        cv2.imwrite("data/test_{0}_{1}.jpg".format(f.frame_id, f.tile_id), f.rawImage)

if __name__ == '__main__':
    test_openhevc_decoder()
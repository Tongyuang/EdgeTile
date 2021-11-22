#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Sunday, July 19th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
import logging

import numpy as np
import cv2

def calculate_psnr(img1, img2, max_value=255):
    """"Calculating peak signal-to-noise ratio (PSNR) between two images."""
    mse = np.mean((np.array(img1, dtype=np.float32) - np.array(img2, dtype=np.float32)) ** 2)
    if mse == 0:
        return 100
    return 20 * np.log10(max_value / (np.sqrt(mse)))

# img1 = cv2.imread('/Users/wangxu/Edge/EdgeTileClient/data/drone/video_2k_120fps/jpg/uav_001.bmp')
# img2 = cv2.imread('/Users/wangxu/jpeg/jpg/uav_0001.jpg')
# img3 = cv2.imread('/Users/wangxu/Edge/EdgeTileClient/data/drone/video_2k_120fps/h264/uav_001.bmp')
# img4 = cv2.imread('/Users/wangxu/Edge/EdgeTileClient/data/drone/video_2k_120fps/hevc/uav_001.bmp')
# print(calculate_psnr(img1, img2)) 
# print(calculate_psnr(img1, img3)) 
# print(calculate_psnr(img1, img4)) 
img2 = cv2.imread('/Users/wangxu/Git/EdgeTile-Client/data/drone/video_2k_120fps/jpg/uav_001_5.jpg')
# cv2.imwrite(str('/Users/wangxu/Git/EdgeTile-Client/data/drone/video_2k_120fps/jpg/uav_001_5_10.jpg'), img2, [int(cv2.IMWRITE_JPEG_QUALITY), 10])
cv2.imwrite(str('/Users/wangxu/Git/EdgeTile-Client/data/drone/video_2k_120fps/jpg/uav_001_5_1.jpg'), img2, [int(cv2.IMWRITE_JPEG_QUALITY), 1])
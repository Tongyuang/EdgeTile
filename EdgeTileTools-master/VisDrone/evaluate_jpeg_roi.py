#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Tuesday, July 21st 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from pathlib import Path
import cv2
import numpy as np

bmp_root = Path('/Users/wangxu/Edge/EdgeTileClient/data/drone/video_2k_120fps/jpg/')

for i in range(1, 38):
    bmp_file = bmp_root / f"uav_{i:03d}.bmp"
    img = cv2.imread(str(bmp_file))
    img_new = np.zeros(img.shape, img.dtype)
    # split to 4 tile
    split_width = 2
    split_height = 2
    split_x = [int(x) for x in np.linspace(0, img.shape[0], split_width + 1)]
    split_y = [int(y) for y in np.linspace(0, img.shape[1], split_height + 1)]
    pred_boxes = []
    for k in range(split_width):
        for j in range(split_height):
            sub_img = img[split_x[k]: split_x[k + 1], split_y[j]: split_y[j + 1], :]
            save_file = bmp_root / f"uav_{i:03d}_part_{k * 2 + j}.jpg"
            if (k + j) % 2 == 0:
                cv2.imwrite(str(save_file), sub_img, [int(cv2.IMWRITE_JPEG_QUALITY), 5])
            else:
                cv2.imwrite(str(save_file), sub_img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            encode_img = cv2.imread(str(save_file))
            img_new[split_x[k]: split_x[k + 1], split_y[j]: split_y[j + 1], :] = encode_img
    compress_img_file = bmp_root / f"uav_{i:03d}_roi.bmp"
    cv2.imwrite(str(compress_img_file), img_new)

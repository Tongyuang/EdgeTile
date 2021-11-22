#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, February 15th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from pathlib import Path
import os
import cv2
from matplotlib import pyplot as plt
import numpy as np

sequence_name = "uav0000137_00458_v"
root_dir = "/Users/wangxu/Downloads/VisDrone2019-MOT-val"
imgs_dir = Path(root_dir) / "sequences" / sequence_name
output_dir = Path(root_dir) / "sequences" / (sequence_name + "_gt")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

anno_path = Path(root_dir) / "annotations" / (sequence_name + ".txt")
category_list = ["ignored regions", "pedestrian", "people", "bicycle", "car", "van",
                 "truck", "tricycle", "awning-tricycle", "bus", "motor" "others"]

cmap = plt.get_cmap("tab20b")
color_list = [cmap(i) for i in np.linspace(0, 1, 20)]


# rgb to bgr
for i, c in enumerate(color_list):
    color_list[i] = (c[2] * 255, c[1] * 255, c[0] * 255)

frames_items = dict()
with open(anno_path, 'r') as f:
    for l in f.readlines():
        item = [int(u) for u in l[:-1].split(',')]
        frame_id = item[0]
        target_id = item[1]
        left = item[2]
        top = item[3]
        width = item[4]
        height = item[5]
        category = item[7]
        if frame_id not in frames_items:
            frames_items[frame_id] = list()
        frames_items[frame_id].append(
            {"l": left, "t": top, "w": width, "h": height, "c": category})
font_scale = 1.5
font = cv2.FONT_HERSHEY_PLAIN

for f, targets in frames_items.items():
    img_path = str(imgs_dir / '{:07d}.jpg'.format(f))
    img = cv2.imread(img_path)
    for t in targets:
        cv2.rectangle(img, (t["l"], t["t"]), (t["l"] +
                                              t["w"], t["t"] + t["h"]), color_list[t["c"]], 2)
        
        text = category_list[t["c"]]
        (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=2)[0]
        cv2.rectangle(img, (t["l"], t["t"]), (t["l"] + text_width, t["t"] + text_height), color_list[t["c"]], cv2.FILLED)
        cv2.putText(img, category_list[t["c"]], (t["l"], t["t"] + text_height),  color=(255, 255, 255), fontFace=font, fontScale=font_scale)
    cv2.imwrite(str(output_dir / '{:07d}.jpg'.format(f)),  img)

#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, April 22nd 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from pathlib import Path
import os
import cv2
from matplotlib import pyplot as plt
import numpy as np
import xml.etree.ElementTree as ET

exp_name = 'both_4d_7'

video_name = 'uav0000137_00458_v'

anno_path = Path('/Users/wangxu/Edge/EdgeTileClient/data/drone/anno720p/') / video_name

img_dir = Path('/Users/wangxu/Edge/EdgeTileClient/data/drone/track') / exp_name

font_scale = 1.5
font = cv2.FONT_HERSHEY_PLAIN

cmap = plt.get_cmap("tab10")
color_list = [cmap(i) for i in np.linspace(0, 1, 10)]


# rgb to bgr
for i, c in enumerate(color_list):
    color_list[i] = (c[2] * 255, c[1] * 255, c[0] * 255)

for img_file in img_dir.glob("**/[0-9][0-9][0-9][0-9][0-9][0-9].jpg"):
    print(img_file)
    anno_file = anno_path / (img_file.stem + '.xml')
    print(anno_file)
    tree = ET.parse(anno_file)
    img = cv2.imread(str(img_file))
    for item in tree.findall(".//object"):
        class_name = item.find("./name").text
        class_name = {'pedestrian':'people', 'car':'car'}[class_name]
        track_id = int(item.find("./trackid").text)
        xmax = float(item.find(".//xmax").text)
        xmin = float(item.find(".//xmin").text)
        ymax = float(item.find(".//ymax").text)
        ymin = float(item.find(".//ymin").text)
        cv2.rectangle(img, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color_list[9], 2)
        
        # text = class_name
        # (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=2)[0]
        # cv2.rectangle(img, (int(xmin), int(ymin)), (int(xmin) + text_width, int(ymin) + text_height), color_list[0], cv2.FILLED)
        # cv2.putText(img, class_name, (int(xmin), int(ymin) + text_height), color=(255, 255, 255), fontFace=font, fontScale=font_scale)
    cv2.imwrite(str(img_file.parent / ("gt_" + img_file.name)), img)
        



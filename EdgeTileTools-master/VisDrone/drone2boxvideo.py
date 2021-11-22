#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Sunday, May 24th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from pathlib import Path
import cv2
from matplotlib import pyplot as plt
import os
import numpy as np
import xml.etree.ElementTree as ET
import time
from xml.dom import minidom


def load_gt(anno_path, frame_id):
    tree = ET.parse(anno_path / '{:06d}.xml'.format(frame_id)) 
    gt_boxes = []
    for item in tree.findall(".//object"):
        class_name = item.find("./name").text
        # class_name = {'pedestrian':'people', 'car':'car'}[class_name]
        track_id = int(item.find("./trackid").text)
        xmax = float(item.find(".//xmax").text)
        xmin = float(item.find(".//xmin").text)
        ymax = float(item.find(".//ymax").text)
        ymin = float(item.find(".//ymin").text)
        gt_boxes.append({'xmax': xmax, 'xmin': xmin, 'ymax': ymax, 'ymin': ymin, 'track_id': track_id, 'class_name': class_name})
    return gt_boxes

video_root = Path('/srv/node/sdd1/VisDrone2019-MOT-val/drone/video_2k_120fps/')
anno_root = Path('/srv/node/sdd1/VisDrone2019-MOT-val/drone/anno_2k_120fps/')
video_name = 'uav0000126_00001_v'
video_path = video_root / f"{video_name}.mp4"
anno_path = anno_root / video_name
output_dir = Path('/srv/node/sdd1/VisDrone2019-MOT-val/drone/video_2k_120fps/') / f"{video_name}_check/"
if not os.path.exists(output_dir):
    os.mkdir(output_dir)    


cap = cv2.VideoCapture(str(video_path))
frame_id = 0
cmap = plt.get_cmap("tab20b")
color_list = [cmap(i) for i in np.linspace(0, 1, 20)]


# rgb to bgr
for i, c in enumerate(color_list):
    color_list[i] = (c[2] * 255, c[1] * 255, c[0] * 255)

font_scale = 1.5
font = cv2.FONT_HERSHEY_PLAIN

while cap.isOpened():
    ret, frame = cap.read()
    if ret == True:
        print(frame_id)
        
        gt_boxes = load_gt(frame_id)
        img = frame
        for t in gt_boxes:
            cv2.rectangle(img, (int(t["xmin"]), int(t["ymin"])), (int(t["xmax"]), int(t["ymax"])), (255, 0, 0), 2)
            
            text = t["class_name"]
            (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=2)[0]
            cv2.rectangle(img, (int(t["xmin"]), int(t["ymin"])), (int(t["xmin"] + text_width), int(t["ymin"] + text_height)), color_list[0], cv2.FILLED)
            cv2.putText(img, text, (int(t["xmin"]), int(t["ymin"] + text_height)),  color=(255, 255, 255), fontFace=font, fontScale=font_scale)
        cv2.imwrite(str(output_dir / '{:06d}.jpg'.format(frame_id * 4)),  img)

        frame_id += 1
    else:
        break
cap.release()
cmd = "ffmpeg -r 30 -i " + str(output_dir) + "/%06d.jpg" + " -c:v libx264  " + str(output_dir / (video_name + "_check.mp4"))
os.system(cmd)
print("finish")


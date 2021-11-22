#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Tuesday, July 21st 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from pathlib import Path
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def write_xml(dst_file, json_content):
    anno = ET.Element('annotation')
    for obj in json_content:
        obj_ele = ET.SubElement(anno, 'object')
        track_id = ET.SubElement(obj_ele, 'trackid')
        track_id.text = str(obj['target_id'])
        name = ET.SubElement(obj_ele, 'name')
        name.text = str(obj['category'])
        bndbox = ET.SubElement(obj_ele, 'bndbox')
        xmin = ET.SubElement(bndbox, 'xmin')
        xmax = ET.SubElement(bndbox, 'xmax')
        ymin = ET.SubElement(bndbox, 'ymin')
        ymax = ET.SubElement(bndbox, 'ymax')
        xmin.text = str(obj['xmin'])
        ymin.text = str(obj['ymin'])
        xmax.text = str(obj['xmax'])
        ymax.text = str(obj['ymax'])

    mydata = ET.tostring(anno, 'utf-8')
    reparsed = minidom.parseString(mydata)
    mydata = reparsed.toprettyxml(indent="\t")
    myfile = open(dst_file, "w")
    myfile.write(mydata)


car_pred_file = Path('/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/car.txt')
person_pred_file = Path('/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/pedestrian.txt')
detect_bboxes = {}
with open(str(car_pred_file), 'r') as f:
    for line in f.readlines():
        line = line.strip('\n')
        vals = line.split(' ')
        frame_id = int(vals[0])
        conf = float(vals[1])
        xmin = max(float(vals[2]), 0)
        ymin = max(float(vals[3]), 0)
        xmax = float(vals[4])
        ymax = float(vals[5])
        print(f"frame id: {frame_id} conf: {conf} xmin: {xmin} ymin: {ymin} xmax: {xmax} ymax: {ymax}")
        if frame_id not in detect_bboxes:
            detect_bboxes[frame_id] = []
        detect_bboxes[frame_id].append({'target_id': -1, 'category': 'car', 'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax})



with open(str(person_pred_file), 'r') as f:
    for line in f.readlines():
        line = line.strip('\n')
        vals = line.split(' ')
        frame_id = int(vals[0])
        conf = float(vals[1])
        xmin = float(vals[2])
        ymin = float(vals[3])
        xmax = float(vals[4])
        ymax = float(vals[5])
        print(f"frame id: {frame_id} conf: {conf} xmin: {xmin} ymin: {ymin} xmax: {xmax} ymax: {ymax}")
        if frame_id not in detect_bboxes:
            detect_bboxes[frame_id] = []
        detect_bboxes[frame_id].append({'target_id': -1, 'category': 'pedestrian', 'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax})

for k, v in detect_bboxes.items():
    save_dir = Path('/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/YOLOv3/uav0000138_00000_v/')
    if not save_dir.exists():
        os.mkdir(str(save_dir))
    dst_file =  save_dir / '{:06d}.xml'.format(k)
    write_xml(str(dst_file), v)
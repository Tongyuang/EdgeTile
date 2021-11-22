#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, March 23rd 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''

from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

def write_xml(dst_file, json_content):
    anno = ET.Element('annotation')
    for obj in json_content:
        obj_ele = ET.SubElement(anno, 'object')
        track_id = ET.SubElement(obj_ele, 'trackid')
        track_id.text = str(obj['target_id'])
        name = ET.SubElement(obj_ele, 'name')
        name.text = "pedestrian"
        occlusion = ET.SubElement(obj_ele, 'occlusion')
        occlusion.text = str(obj['occlusion'])
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

mot_root = Path("/Users/wangxu/Edge/EdgeTileClient/data/mot17/raw/MOT17/train/")
data_root = Path('/Users/wangxu/Git/EdgeTile-Client/data')
for anno_file in mot_root.glob("**/*FRCNN/gt/gt.txt"):
    frame_objects = {}
    video_name = anno_file.parts[10]
    print(video_name)
    with open(anno_file) as f:
        for l in f.readlines():
            item = [float(u) for u in l[:-1].split(',')]
            frame_id = item[0]
            target_id = int(item[1])
            left = item[2]
            top = item[3]
            width = item[4]
            height = item[5]
            flag = item[6]
            type = item[7]
            occlusion = item[8]
            if flag == 1:
                if type != 1:
                    print("error", type)
                if frame_id not in frame_objects:
                    frame_objects[frame_id] = []
                frame_objects[frame_id].append({'target_id': target_id, 'xmin': left, 'ymin': top, 'xmax': left + width, 'ymax': top + height, 'occlusion': occlusion})
    seq_dir = data_root / 'mot17' / 'anno' / video_name
    if not os.path.exists(seq_dir):
        os.mkdir(seq_dir)
    for frame_id, objs in frame_objects.items():
        dst_file = seq_dir / '{:06d}.xml'.format(int(frame_id) - 1)
        write_xml(dst_file, objs)
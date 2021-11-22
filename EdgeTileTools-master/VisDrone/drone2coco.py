#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, February 17th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
# visdrone to coco format
from pathlib import Path
import os
import cv2
import json
import imagesize
import shutil

data_root = '/Users/wangxu/Git/EdgeTile-Client/data'
coco_dir = Path(data_root) / 'coco'
if not os.path.exists(coco_dir):
    os.mkdir(coco_dir)
anno_dir = coco_dir / 'annotations'
if not os.path.exists(anno_dir):
    os.mkdir(anno_dir)

img_dir = coco_dir / 'test2020'
if not os.path.exists(img_dir):
    os.mkdir(img_dir)

anno_json = anno_dir / 'test2020.json'

drone_root = Path("/Users/wangxu/Downloads/VisDrone2019-MOT-test-dev/")

anno_data = dict()
anno_data["info"] = {"year": 2020, "version": 0.1, "description": "visdrone dataset", "contributor": "", "url": "", "date_created": "2020-02-17"}
anno_data["licenses"] = []
anno_data["categories"] = [{"id": 0, "name": "ignored regions", "supercategory": ""},
                           {"id": 1, "name": "pedestrian", "supercategory": ""},
                           {"id": 2, "name": "people", "supercategory": ""},
                           {"id": 3, "name": "bicyle", "supercategory": ""},
                           {"id": 4, "name": "car", "supercategory": ""},
                           {"id": 5, "name": "van", "supercategory": ""},
                           {"id": 6, "name": "truck", "supercategory": ""},
                           {"id": 7, "name": "tricycle", "supercategory": ""},
                           {"id": 8, "name": "awning-tricycle", "supercategory": ""},
                           {"id": 9, "name": "bus", "supercategory": ""},
                           {"id": 10, "name": "motor", "supercategory": ""},
                           {"id": 11, "name": "others", "supercategory": ""}]

anno_data["images"] = []
anno_data["annotations"] = []
img_ids_mapping = {}
for img_id, img in enumerate(drone_root.glob("**/*.jpg")):
    width, height = imagesize.get(str(img))
    dst_img = img.parent.stem + img.name
    shutil.move(str(img), img_dir / dst_img)
    img_ids_mapping[dst_img] = img_id
    anno_data["images"].append({"id": img_id, "width": width, "height": height, "file_name": dst_img, "license": "", "date_captured": ""})
anno_id = 0
for anno_file in drone_root.glob("**/*.txt"):
    with open(anno_file) as f:
        for l in f.readlines():
            item = [int(u) for u in l[:-1].split(',')]
            frame_id = item[0]
            target_id = item[1]
            left = item[2]
            top = item[3]
            width = item[4]
            height = item[5]
            category = item[7]
            dst_img_name = anno_file.stem + "{:07d}.jpg".format(frame_id)
            anno_data["annotations"].append({"id": anno_id, "image_id": img_ids_mapping[dst_img_name], "category_id": category, "segmentation": "", "area": width * height, "bbox": [left, top, width, height], "iscrowd": 0})
            anno_id += 1

json.dump(anno_data, open(anno_json, 'w'), indent=4)




 








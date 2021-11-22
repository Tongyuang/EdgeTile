#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, November 18th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import cv2
import numpy as np
import xml.etree.ElementTree as ET
import pathlib

from config.load_config import global_config
from core.bbox_object import BBoxObject
from collections import namedtuple
Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')

def intersect_area(a, b):  # returns None if rectangles don't intersect
    dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
    dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
    if (dx>=0) and (dy>=0):
        return dx*dy
    return 0

# the frame object contains the raw frame data, so will be free while reading video
# the frame property will be hold all the time
class Frame:
    def __init__(self, video_path, frame_idx, raw_frame, width, height):
        super().__init__()
        self.frame_property = FrameProperty(video_path, frame_idx, width, height)
        self.raw_frame = raw_frame
        self.yuv_frame = None

    def convert_yuv(self):
        yuv_data = cv2.cvtColor(self.raw_frame, cv2.COLOR_BGR2YUV_I420)
        (h, w, c) = self.raw_frame.shape
        y = np.reshape(yuv_data[0:h, :], (-1, 1))
        u = np.reshape(yuv_data[h:int(h + h / 4), :], (-1, 1))
        v = np.reshape(yuv_data[int(h + h / 4):, :], (-1, 1))
        self.yuv_frame = [y, u, v]

class FrameProperty:
    def __init__(self, video_path, frame_idx, width, height):
        super().__init__()
        self.frame_idx = frame_idx
        self.video_path = video_path
        self.w = width
        self.h = height
        self.bbox = list()
        self.server_bbox = list()
        self.client_bbox = list()
        self.will_upload = False
        self.cache_time = None
        self.in_blacklist = True

    def load_bbox(self, anno_path):
        frame_anno_path = anno_path / "{:06d}.xml".format(self.frame_idx)

        tree = ET.parse(frame_anno_path)
        for item in tree.findall(".//object"):
            bbox_item = BBoxObject()
            bbox_item.class_name = item.find("./name").text
            bbox_item.track_id = int(item.find("./trackid").text)
            bbox_item.xmax = float(item.find(".//xmax").text)
            bbox_item.xmin = float(item.find(".//xmin").text)
            bbox_item.ymax = float(item.find(".//ymax").text)
            bbox_item.ymin = float(item.find(".//ymin").text)
            bbox_item.confidence = 1.0
            self.bbox.append(bbox_item)

    def load_local_bbox(self, anno_path):
        frame_anno_path = anno_path / "{:06d}.xml".format(self.frame_idx)

        tree = ET.parse(frame_anno_path)
        for item in tree.findall(".//object"):
            bbox_item = BBoxObject()
            bbox_item.class_name = item.find("./name").text
            bbox_item.track_id = int(item.find("./trackid").text)
            bbox_item.xmax = float(item.find(".//xmax").text)
            bbox_item.xmin = float(item.find(".//xmin").text)
            bbox_item.ymax = float(item.find(".//ymax").text)
            bbox_item.ymin = float(item.find(".//ymin").text)
            bbox_item.confidence = 1.0
            self.client_bbox.append(bbox_item)

    def load_server_bbox(self, anno_path):
        frame_anno_path = anno_path / "{:06d}.xml".format(self.frame_idx)

        tree = ET.parse(frame_anno_path)
        for item in tree.findall(".//object"):
            bbox_item = BBoxObject()
            bbox_item.class_name = item.find("./name").text
            bbox_item.track_id = int(item.find("./trackid").text)
            bbox_item.xmax = float(item.find(".//xmax").text)
            bbox_item.xmin = float(item.find(".//xmin").text)
            bbox_item.ymax = float(item.find(".//ymax").text)
            bbox_item.ymin = float(item.find(".//ymin").text)
            bbox_item.confidence = 1.0
            self.server_bbox.append(bbox_item)


    def box2dict(self, filter=None):
        boxes = dict()
        boxes['frame_id'] = self.frame_idx
        boxes['boxes'] = []
        for box in self.bbox:
            if filter:
                ra = Rectangle(box.xmin, box.ymin, box.xmax, box.ymax)
                center_x = int((box.xmin+box.xmax)/2)
                center_y = int((box.ymin+box.ymax)/2)
                # rb = Rectangle(filter[0], filter[1], filter[0] + filter[2], filter[1] + filter[3])
                border_xmin = filter[0]
                border_ymin = filter[1]
                border_xmax = filter[0] + filter[2]
                border_ymax = filter[1] + filter[3]
                if center_x >= border_xmin and center_x < border_xmax and center_y >= border_ymin and center_y < border_ymax:
                    boxes['boxes'].append({'xmin': box.xmin, 'xmax': box.xmax, 'ymin': box.ymin, 'ymax': box.ymax, 'class_name': box.class_name, 'confidence': box.confidence})

                # it = intersect_area(ra, rb) / ((box.xmax - box.xmin) * (box.ymax - box.ymin))
                # if it > 0.4:
                #     boxes['boxes'].append({'xmin': box.xmin, 'xmax': box.xmax, 'ymin': box.ymin, 'ymax': box.ymax, 'class_name': box.class_name, 'confidence': box.confidence})
            else:
                boxes['boxes'].append({'xmin': box.xmin, 'xmax': box.xmax, 'ymin': box.ymin, 'ymax': box.ymax, 'class_name': box.class_name, 'confidence': box.confidence})
        return boxes

def test_xml():
    tree = ET.parse("/Users/wangxu/Git/EdgeTile-Client/data/ILSVRC_sample/anno/ILSVRC2015_val_00000000/000041.xml")

    for item in tree.findall("//object"):
        track_id = item.find("./trackid").text
        xmax = item.find(".//xmax").text
        xmin = item.find(".//xmin").text
        ymax = item.find(".//ymax").text
        ymin = item.find(".//ymin").text

if __name__ == "__main__":
    test_xml()





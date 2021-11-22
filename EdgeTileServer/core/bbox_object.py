#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, November 21st 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
class BBoxObject:
    def __init__(self):
        super().__init__()
        self.class_name = None
        self.xmin = 0
        self.xmax = 0
        self.ymin = 0
        self.ymax = 0
        self.track_id = 0
        self.confidence = 0

    def from_dict(self, dict_obj):
        attrs = ['class_name', 'xmin', 'xmax', 'ymin', 'ymax', 'track_id', 'confidence']
        for attr in attrs:
            if attr in dict_obj:
                setattr(self, attr, dict_obj[attr])
    
    def to_tuple(self):
        return (self.xmin, self.ymin, self.xmax - self.xmin, self.ymax - self.ymin)
    
    def from_tuple(self, val):
        self.xmin = val[0]
        self.ymin = val[1]
        self.xmax = val[0] + val[2]
        self.ymax = val[1] + val[3]
    
    def calculate_iou(self, box):
        x = max(self.xmin, box.xmin)
        y = max(self.ymin, box.ymin)
        w = min(self.xmax, box.xmax) - x
        h = min(self.ymax, box.ymax) - y
        if w < 0 or h < 0:
            return 0
        ia = w * h
        sa = (self.xmax - self.xmin) * (self.ymax - self.ymin)
        ba = (box.xmax - box.xmin) * (box.ymax - box.ymin)
        return ia / (sa + ba - ia)
        
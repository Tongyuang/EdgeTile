#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, November 28th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import sys
sys.path.insert(0, "dist/python3")
import cv2

from core.models.model import Model
from core.bbox_object import BBoxObject

class OpencvTracker(Model):
    def __init__(self, component):
        super().__init__(component, "opencv_tracker")
    
    def _initialize(self):
        self.tracker = None
        self.refer_frame = None

    def init_tracker(self, refer_frame):
        # if the refer_frame is None or refer_frame has been updated in frame cache then reinit tracker
        if (not self.refer_frame) or (self.refer_frame.frame_property.frame_idx != refer_frame.frame_property.frame_idx):
            self.logger.info("reset tracker...")
            tracker_name = self.config['tracker']
            self.refer_frame = refer_frame
            self.tracker = cv2.MultiTracker_create()
            for box in self.refer_frame.frame_property.server_bbox:
                tr = None
                if tracker_name.upper() == 'KCF':
                    tr = cv2.TrackerKCF_create()
                self.tracker.add(tr, self.refer_frame.raw_frame, box.to_tuple())
    
    def detect(self, frame):
        refer_frame = self.component.app.cache.refer_frame
        if refer_frame:
            self.init_tracker(refer_frame)
        ok, boxes = self.tracker.update(frame.raw_frame)
        for i, box in enumerate(boxes):
            b = BBoxObject()
            b.from_tuple(box)
            b.class_name = refer_frame.frame_property.server_bbox[i].class_name
            b.confidence = refer_frame.frame_property.server_bbox[i].confidence
            frame.frame_property.client_bbox.append(b)
        # self.component.logger.info(f"*predict frame: {frame.frame_property.frame_idx} boxes: {frame.frame_property.client_bbox.}")
       

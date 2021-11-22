#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Sunday, November 24th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import cv2
from core.models.model import Model

class OpticalFlow(Model):
    def __init__(self, component):
        super().__init__(component, "optical_flow")
    
    def _initialize(self):
        pass
    
    def detect(self, frame):
        refer_frame = self.component.app.cache.refer_frame
        if not refer_frame:
            return
            
    def predict(self, reference_frame, reference_bbox, current_frame):
        # cur_det_kps, status, err = cv2.calcOpticalFlowPyrLK(prev_frame, cur_frame,
        #                                                             det_kps, None,
        #                                                             winSize=(31, 31), maxLevel=3,
        #                                                             criteria=(
        #                                                                 cv2.TermCriteria_MAX_ITER | cv2.TermCriteria_EPS,
        #                                                                 10, 0.03),
        #                                                             flags=0, minEigThreshold=0.01
        #                                                             )
        pass
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, November 27th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import pathlib
import time
from config.load_config import load_config

from core.frame import Frame as UploadFrame

class FakeDetection:
    def __init__(self, pid):
        config = load_config()
        self.config = config['server']['model']['fake_detection']
        self.pid = pid
        self.video_name = ""
        print(f"start fake detection: {pid}")
    
    def _initialize(self):
        
        pass
    
    def detect(self, frame_obj, server_boxes):
        # self.video_path = pathlib.Path(self.config['video']) / self.component.app.get_video_property().video_name
        print(f"start detect {frame_obj['frame_id']} frame")
        self.video_name = frame_obj["video_name"]
        self.anno_path = pathlib.Path(self.config['anno']) / self.video_name
        f = UploadFrame(self.video_name, frame_obj['frame_id'], frame_obj['img'], self.config["video_width"], self.config["video_height"])
        # f.frame_property.load_bbox(anno_path=self.anno_path)
        for box in server_boxes[frame_obj['frame_id']]:
            f.frame_property.bbox.append(box)

        print("start sleep")
        time.sleep(float(self.config['latency']) / 1000)
        filter_rect = None
        if frame_obj['level'] == 'group':
            filter_rect = frame_obj['rect']
        x = f.frame_property.box2dict(filter=filter_rect)
        print("detect cost times")
        
        return x

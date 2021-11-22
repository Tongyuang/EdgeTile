#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, November 27th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from core.edge_queue import EdgeQueue
from core.edge_component import EdgeComponent
from core.models.optical_flow import OpticalFlow
from core.models.opencv_tracker import OpencvTracker

class EdgeModel(EdgeComponent):
    def __init__(self, app):
        super().__init__(app, "model")
    
    def _initialize(self):
        select_model = self.config['select_model']
        self.model = None
        if select_model == 'optical_flow':
            self.model = OpticalFlow(self)
        elif select_model == 'opencv_tracker':
            self.model = OpencvTracker(self)
        self.model.init()
        self.detect_cache = EdgeQueue(self, "detect_cache")

    
    def run(self):
        while not self.stopped():
            f = self.detect_cache.get()
            if type(f) == str:
                if self.app.get_video_player():
                    self.app.video_player.render_queue.put(f)
                break
            else:
                if self.app.cache.refer_frame:
                    f.frame_property.in_blacklist = False
                    self.logger.info(f"*bbox_track_start frame: {f.frame_property.frame_idx}")
                    self.model.detect(f)
                    self.logger.info(f"*bbox_track_end frame: {f.frame_property.frame_idx}")
            if self.app.get_video_player():
                self.app.video_player.render_queue.put(f)
        
        self.logger.info("model thread exit...")
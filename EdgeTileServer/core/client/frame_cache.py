#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, November 18th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import pathlib 

from core.edge_queue import EdgeQueue
from utils.utils import get_ms_time, sleep_ms_time
from core.edge_component import EdgeComponent
from core.bbox_object import BBoxObject
from core.edge_evaluator import PerformanceEvaluator

class FrameCache(EdgeComponent):
    def __init__(self, app):
        super().__init__(app, 'cache')
    
    def _initialize(self):
        self.frame_property_cache = list()
        self.raw_cache = EdgeQueue(self, "raw_cache")
        self.upload_cache = list()
        self.refer_frame = None
        self.synthetic_frame = None
        self.evaluator = PerformanceEvaluator(self.app.config['client']['dataset']['validate_set'], \
            self.app.config['client']['dataset']['class_list'], self.app.config['client']['dataset']['labels'])

    def add_frame(self, f):
        if type(f) != str:
            f.cache_time = get_ms_time()
        self.raw_cache.put(f)
    
    def update_from_server(self, server_detions):
        if server_detions['level'] == 'frame':
            while True:
                try:
                    item = self.upload_cache[0]
                except Exception as e:
                    self.logger.error("upload cache error")
                if item.frame_property.frame_idx < server_detions['frame_id']:
                    # drop old cache
                    self.upload_cache.pop(0)
                if item.frame_property.frame_idx > server_detions['frame_id']:
                    self.logger.error("You should check upload cache")
                    break
                if item.frame_property.frame_idx == server_detions['frame_id']:
                    for box in server_detions['boxes']:
                        b = BBoxObject()
                        b.from_dict(box)
                        item.frame_property.server_bbox.append(b)
                    self.refer_frame = item
                    break        

    def run(self):
        while not self.stopped():
            try:
                f = self.raw_cache.get(timeout=10)
                if type(f) == str:
                    video_streamer_config = self.app.video_streamer.config
                    video_name = pathlib.Path(video_streamer_config['video_path']).stem
                    pred_file = pathlib.Path(self.config['eval_dir']) / (video_name + "_pred.txt")
                    blacklist_file = pathlib.Path(self.config['eval_dir']) / (video_name + "_blacklist.txt")
                    self.evaluator.generate_predict_file(self.frame_property_cache, pred_file, blacklist_file)
                    self.app.model.detect_cache.put(f)
                    self.app.socket.close()
                    break
                else:
                    if f.frame_property.will_upload == True:
                        self.upload_cache.append(f)
                    self.logger.info("load bbox start")
                    f.frame_property.load_bbox()
                    self.logger.info("load bbox end")
                    self.frame_property_cache.append(f.frame_property)
                    # update from server
                    
                    self.app.model.detect_cache.put(f)
                
            except Exception as e:
                print(e)
                self.app.stop()
        self.logger.info("cache thread exit...")
            
    def update_synthetic_frame(self, det_box):
        pass

        


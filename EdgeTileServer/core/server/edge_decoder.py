#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, November 21st 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import sys
sys.path.insert(0, "dist/python3")
import math
import cv2
import re
import pathlib
import numpy as np

from core.edge_queue import EdgeQueue
from core.edge_component import EdgeComponent
from core.video_property import VideoProperty


class EdgeDecoder(EdgeComponent):
    def __init__(self, app):
        super().__init__(app, 'decoder')
        
    def _initialize(self):
        self.decoder = cv2.openhevc_decoder_OpenHEVCDecoder()
        self.video_property = None

    def run(self):
        print("before run decoder")
        self.decoder.start(self.config['port'])
        videoProperty = self.decoder.readVideoProperty()
        self.logger.info(f"receive video: {videoProperty.video_name}")
        self.video_property = VideoProperty(videoProperty.video_name, videoProperty.video_width, videoProperty.video_height, videoProperty.tile_width, videoProperty.tile_height)
        
        while not self.stopped():
            f = self.decoder.read()
            self.app.cache.add_frame(f)
            if f.frame_id == -1 and f.tile_id == -1:
                self.logger.info("decoder thread exit...")
                break
            self.logger.info(f"*tile_read frame: {f.frame_id} tile: {f.tile_id} group: {f.groupId}")
            # video_name = self.video_property.video_path.stem
            # save_path = pathlib.Path(self.config['img_path']) / "{2}_{0}_{1}.jpg".format(f.frame_id, f.tile_id, video_name)
            # save_path = "{2}_{0}_{1}.jpg".format(f.frame_id, f.tile_id, video_name) 
            # self.logger.info("save image: {}".format(save_path))
            # cv2.imwrite(str(save_path), f.rawImage)
          

    

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
import cv2
import pathlib
from enum import Enum
import time

from core.client.video_streaming import VideoStreamerStatus
from core.edge_component import EdgeComponent

class EncoderStatus(Enum):
    ENCODER_BUSY = 0
    ENCODER_IDLE = 1

class EdgeEncoder(EdgeComponent):

    def __init__(self, app):
        super().__init__(app, 'encoder')
        
    # You cannot initialize encoder in __init__ as encoder may not have set video_streamer 
    def _initialize(self):
        video_streamer_config = self.app.video_streamer.config
        video_name = pathlib.Path(video_streamer_config['video_path']).name
        self.encoder = cv2.kvazaar_encoder_KvazaarEncoder(video_name)
        if self.config["mode"] == "SERVER_MODE":
            self.encoder.setServerMode(self.config['ip_addr'], self.config['port'])
        elif self.config["mode"] == "LOCAL_FILE_MODE":
            hevc_folder = pathlib.Path(self.config['hevc_folder'])
            self.encoder.setFileMode(str(hevc_folder / video_name))
        
    def run(self):
        if not self.is_init():
            self.logger("encoder must be initiazed first...")
            return
        if not self.app.video_streamer.is_init():
            self.logger("video streamer must be initiazed first...")
        
        self.encoder.start(self.app.video_streamer.frame_width, self.app.video_streamer.frame_height, 10, self.config['tile_split'], self.config['nthreads'], self.config['quality'])
        while not self.stopped():
            f = self.app.video_streamer.pop_frame()
            if f:
                try:
                    if type(f) == str:
                        self.encoder.stop()
                        #wait for encoder to stop
                        while self.encoder.getEncodeStatus() != -1:
                            time.sleep(0.1)
                        self.app.cache.add_frame(f)
                        break
                    else:
                        encoder_status = self.encoder.encode(f.yuv_frame[0], f.yuv_frame[1], f.yuv_frame[2], f.frame_property.frame_idx)
                        if EncoderStatus(encoder_status.encoderState) == EncoderStatus.ENCODER_IDLE:
                            f.frame_property.will_upload = True
                        self.app.cache.add_frame(f)
                except Exception as e:
                    self.logger.error("error in encoder")
                    self.app.stop()
            
        self.logger.info("encoder thread exit...")

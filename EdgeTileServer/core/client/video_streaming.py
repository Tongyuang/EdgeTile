#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, November 18th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import cv2
import logging
import threading
import time
from enum import Enum

from core.edge_queue import EdgeQueue
from core.frame import Frame as VideoFrame
from utils.utils import get_ms_time, sleep_ms_time
from core.edge_component import EdgeComponent

class VideoStreamerStatus(Enum):
    VIDEO_STRAEMER_UNPLAY = 0
    VIDEO_STREAMER_ISPLAY = 1

class VideoStreamer(EdgeComponent):
    def __init__(self, app):
        super().__init__(app, 'video_streamer')
               
    def _initialize(self):
        self.video_path = self.config['video_path']
        self.cap = cv2.VideoCapture(self.video_path)
        # get video basic info
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0 
        self.read_frames = 0
        self.frame_queue = EdgeQueue(self, "frame_queue")
        self.basic_video_parameters()
        self.status = VideoStreamerStatus.VIDEO_STRAEMER_UNPLAY

    def basic_video_parameters(self):
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.logger.info(f"video property width: {self.frame_width} height: {self.frame_height} fps: {self.fps}")

    def run(self):
        self.logger.info("video streamer starts play...")
        self.status = VideoStreamerStatus.VIDEO_STREAMER_ISPLAY
        self.logger.debug("Frame rate: {}fps".format(self.fps))
        frame_interval = 1000.0 / 30 # millisecond
        
        while not self.stopped():
            start = get_ms_time()
            if not self.next_frame():
                self.status = VideoStreamerStatus.VIDEO_STRAEMER_UNPLAY
                self.frame_queue.put("video streamer exit")
                break
            end = get_ms_time()
            passed = end - start
            remain = frame_interval - passed
            self.logger.info("next frame for {} milliseconds".format(passed))
            if remain > 0:
                self.logger.info("sleep for {} milliseconds".format(remain))
                sleep_ms_time(remain)
            if self.read_frames % 10 == 0:
                self.logger.info("have read {} frames".format(self.read_frames))
        self.logger.debug("Thread finished, reading video stream.")        

    def next_frame(self):
        status, frame = self.cap.read()
        if status:
            fr = VideoFrame(self.video_path, self.read_frames, frame, self.frame_width, self.frame_height)
            fr.convert_yuv()
            self.frame_queue.put(fr)
           
        self.read_frames += 1
        return status

    def reset(self):
        if self.status != VideoStreamerStatus.VIDEO_STRAEMER_UNPLAY:
            self.logger.error("must stop play before reset")
        else:
            self.logger.info("video streamer is reset")
            self.cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
            self.read_frames = 0
    
    def pop_frame(self):
        try:
            frame = self.frame_queue.get(block=True, timeout=10)
            # self.logger.info("pop frame")
            return frame
        except:
            self.logger.debug("pop frame timeout")
        return None

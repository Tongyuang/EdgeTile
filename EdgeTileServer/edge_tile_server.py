#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, November 20th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import time
import numpy as np
import os

from config.load_config import load_config
from utils.custom_logging import get_logger
from core.server.edge_decoder import EdgeDecoder
from core.server.edge_socket import EdgeSocket
from core.server.frame_cache import FrameCache
from core.server.edge_model import EdgeModel
from core.edge_app import EdgeApp
from core.edge_evaluator import TimeEvaluatorManager
import multiprocessing as mp

class EdgeTileServer(EdgeApp):
    def __init__(self):
        super().__init__('server', 'EdgeTileServer')
    
    def start(self):
        # start
        self.manager = TimeEvaluatorManager()
        self.register('decoder', EdgeDecoder)
        self.register('socket', EdgeSocket)
        self.register('cache', FrameCache)
        self.register('model', EdgeModel)
        self.initialize()
        self.start_components()
        self.join()
    
    def get_video_property(self):
        if self.decoder:
            return self.decoder.video_property
        return None
    
    def get_tile_count(self):
        if self.decoder:
            return self.decoder.video_property.tile_width * self.decoder.video_property.tile_height
        else:
            return None

    def get_tiles_position(self):
        if self.decoder and self.decoder.video_property:
            return self.decoder.video_property.tiles_position
    
    def stop(self):
        # self.manager.evaluate()
        super().stop()
        # os._exit(0)
        

if __name__ == '__main__':
    mp.set_start_method('spawn')
    server = EdgeTileServer()
    server.start()

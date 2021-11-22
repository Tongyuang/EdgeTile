#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Friday, November 22nd 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''

from core.edge_component import EdgeComponent
from core.edge_queue import EdgeQueue
from core.edge_evaluator import TimeEvaluator
from core.group_tile import GroupTile


class FrameCache(EdgeComponent):
    def __init__(self, app):
        super().__init__(app, 'cache')
    
    def _initialize(self):
        self.evaluator = TimeEvaluator(self, "merge frame evaluator")
        self.raw_cache = EdgeQueue(self, 'raw_cache', max_size=-1)
        self.video_property = None
        self.is_initialized = True

    def set_video_property(self, video_property):
        self.video_property = video_property
        self.logger.info("set video property")

    def add_frame(self, f):
        self.raw_cache.put(f)

    def run(self):
        group_tiles = {}
        while not self.stopped():
            try:
                tile = self.raw_cache.get()
                if tile.frame_id == -1 and tile.tile_id == -1:
                    self.logger.info("cache thread exit...")
                    self.app.model.detect_cache.put({'frame_id': -1})
                    break
                # tile_count = self.video_property.tile_split[0] * self.video_property.tile_split[1]
                if tile.groupId not in group_tiles:
                    group_tiles[tile.groupId] = GroupTile(self.app)
                group_tiles[tile.groupId].add_tile(tile)
                if group_tiles[tile.groupId].is_group_full():
                    group_tiles[tile.groupId].merge(write_disk=False)
                    group_tiles[tile.groupId].wait_for_detect()
                    del group_tiles[tile.groupId]
                    
            except Exception as e:
                print(e.args)
                print(e)
                self.app.stop()
                # merge tiles

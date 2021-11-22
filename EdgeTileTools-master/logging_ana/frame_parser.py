#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, November 30th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from collections import OrderedDict

from log_parser import LogParser
from tile_parser import TileParser
from utils.utils import mstimestamp_to_str

class FrameParser(LogParser):
    def __init__(self, idx):
        super().__init__()
        self.key_idx = "Frame " + str(idx)
        self.tiles = dict()
    
    def parse(self, dict_data):
        handle_types = ['feed', 'render', 'bbox_send', 'bbox_recv', \
            'bbox_infer_start', 'bbox_infer_end', 'bbox_track_start', 'bbox_track_end', \
                'tile_merge_start', 'tile_merge_end', 'updoad_frame']
        if dict_data['type'] in handle_types:
            self.set_attr(dict_data['type'] + '_time', mstimestamp_to_str(dict_data['time']))
        
        if 'tile' in dict_data:
            if dict_data['tile'] >= 0:
                if dict_data['tile'] not in self.tiles:
                    tile = TileParser(dict_data['tile'])
                    self.tiles[dict_data['tile']] = tile
                tile = self.tiles[dict_data['tile']]
                tile.parse(dict_data)
    
    def get_tile(self, i):
        return self.get_attr("Tile " + str(i))
    
    def prepare_dump(self):
        # handle_types = ['feed_time', 'render_time', 'bbox_send_time', 'bbox_recv_time', \
        #     'bbox_infer_start_time', 'bbox_infer_end_time', 'bbox_track_start_time', 'bbox_track_end_time', \
        #         'tile_merge_start_time', 'tile_merge_end_time']
        # frame_dict = OrderedDict()
        # for key in handle_types:
        #     frame_dict[key] = getattr(self, key)
        tiles = [(k, v) for k, v in self.tiles.items()]
        tiles.sort(key=lambda x:x[0])
        for _, tile in tiles:
            self.set_attr(tile.key_idx, tile.dump())

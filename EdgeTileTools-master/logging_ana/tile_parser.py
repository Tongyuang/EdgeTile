#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, November 30th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from collections import OrderedDict
import datetime

from log_parser import LogParser
from utils.utils import mstimestamp_to_str

class TileParser(LogParser):
    def __init__(self, idx):
        super().__init__()
        self.key_idx = "Tile " + str(idx)
        
        # self.tile_size = None
        # self.tile_recv_start_time = None
        # self.tile_recv_end_time = None
        # self.tile_send_start_time = None
        # self.tile_send_end_time = None
        # self.tile_decode_time = None
        # self.tile_convert_time = None
        # self.tile_read_time = None

    def parse(self, dict_data):
        handle_types = ['tile_send_start', 'tile_send_end', 'tile_recv_start', 'tile_recv_end', 'tile_decode', 'tile_read', 'tile_convert']
        if dict_data['type'] in handle_types:
            self.set_attr(dict_data['type'] + '_time', mstimestamp_to_str(dict_data['time']))

        handle_types = {'tile_send_start': ('size', 'tile_size')}
        if dict_data['type'] in handle_types.keys():
            log_key = handle_types[dict_data['type']][0]
            attr_key = handle_types[dict_data['type']][1] 
            self.set_attr(attr_key, dict_data[log_key])
    
    # def dump(self):
    #     tile_dict = OrderedDict()
    #     keys = ['tile_send_start_time', 'tile_send_end_time', 'tile_recv_start_time', 'tile_recv_end_time', 'tile_decode_time', 'tile_read_time', 'tile_size', 'tile_convert_time']
    #     for key in keys:
    #         tile_dict[key] = getattr(self, key)
    #     return tile_dict
    def prepare_dump(self):
        pass

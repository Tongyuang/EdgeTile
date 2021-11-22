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
from frame_parser import FrameParser

class VideoParser(LogParser):
    def __init__(self):
        super().__init__()
        self.frames = dict()

    def parse(self, log_data):
        for dict_data in log_data:
            # print(dict_data)
            if 'frame' in dict_data:
                if dict_data['frame'] not in self.frames:
                    frame = FrameParser(dict_data['frame'])
                    self.frames[dict_data['frame']] = frame
                frame = self.frames[dict_data['frame']]
                frame.parse(dict_data)


    def prepare_dump(self):
        frames_pair = [(k, v) for k, v in self.frames.items()]
        # sort by frame id
        frames_pair.sort(key=lambda x:x[0])
        # video_dict = OrderedDict()
        for _, frame in frames_pair:
            self.set_attr(frame.key_idx, frame.dump())
        

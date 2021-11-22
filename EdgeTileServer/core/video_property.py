#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, November 25th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import math
import numpy as np

class VideoProperty:
    def __init__(self, video_name, w, h, tw, th):
        self.video_name = video_name
        self.width = w
        self.height = h
        self.tile_width = tw
        self.tile_height = th
        self.tiles_position = None
        self.calculate_tile_position()
    
    def calculate_tile_position(self):
        width_lcu_count = math.ceil(self.width / 64)
        height_lcu_count = math.ceil(self.height / 64)
        tiles_width = [0] * self.tile_width
        tiles_height = [0] * self.tile_height
        for i in range(self.tile_width):
            tiles_width[i] = int(
                (i + 1) * width_lcu_count / self.tile_width) - int(i * width_lcu_count / self.tile_width)
        for i in range(self.tile_height):
            tiles_height[i] = int(
                (i + 1) * height_lcu_count / self.tile_height) - int(i * height_lcu_count / self.tile_height)
        tiles_x_pos = [0] * self.tile_width
        tiles_y_pos = [0] * self.tile_height
        for i in range(1, self.tile_width):
            tiles_x_pos[i] = tiles_x_pos[i - 1] + tiles_width[i - 1]
        for i in range(1, self.tile_height):
            tiles_y_pos[i] = tiles_y_pos[i - 1] + tiles_height[i - 1]
        tiles_x_pos = [x_pos * 64 for x_pos in tiles_x_pos]
        tiles_y_pos = [y_pos * 64 for y_pos in tiles_y_pos]
        self.tiles_position = []
        for j in range(self.tile_height):
            for i in range(self.tile_width):
                tile_position = {'x': tiles_x_pos[i],
                                  'y': tiles_y_pos[j], 
                                  'w': min(tiles_width[i] * 64, self.width - tiles_x_pos[i]),
                                  'h': min(tiles_height[j] * 64, self.height - tiles_y_pos[j]),
                                  }
                self.tiles_position.append(tile_position)
        
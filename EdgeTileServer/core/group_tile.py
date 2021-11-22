#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Friday, April 10th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
import numpy as np
import pathlib
import cv2


class GroupTile:
    def __init__(self, app):
        super().__init__()
        self.groupId = -1
        self.groupWidth = 0
        self.groupHeight = 0
        self.groupSize = 0
        self.frame_id = -1
        self.app = app
        self.tiles = []
        self.raw_img = None
        self.rect = None

    def add_tile(self, tile):
        if self.groupId == -1:
            self.groupId = tile.groupId
            self.frame_id = tile.frame_id
            self.groupWidth = tile.groupSize >> 8
            self.groupHeight = tile.groupSize - (self.groupWidth << 8)
            self.groupSize = self.groupHeight * self.groupWidth
            self.app.logger.info(f"frame: {tile.frame_id} tile: {tile.tile_id} groupWidth: {self.groupWidth} "
                                 f"groupHeight: {self.groupHeight}")
        else:
            assert (tile.frame_id == self.frame_id and tile.groupId == self.groupId)
        self.tiles.append(tile)

    def is_group_full(self):
        return len(self.tiles) == self.groupSize

    def merge(self, write_disk):
        assert (self.is_group_full())
        self.tiles.sort(key=lambda x: x.tile_id)
        first_pos = self.app.get_tiles_position()[self.tiles[0].tile_id]
        last_pos = self.app.get_tiles_position()[self.tiles[-1].tile_id]
        w = last_pos['x'] + last_pos['w'] - first_pos['x']
        h = last_pos['y'] + last_pos['h'] - first_pos['y']
        self.rect = (first_pos['x'], first_pos['y'], w, h)
        self.raw_img = np.zeros((h, w, 3))
        self.app.logger.info(f"*tile_merge_start frame: {self.frame_id} group: {self.groupId}")

        for item in self.tiles:
            pos = self.app.get_tiles_position()[item.tile_id]
            self.raw_img[(pos['y'] - first_pos['y']): (pos['y'] - first_pos['y'] + pos['h']),
            (pos['x'] - first_pos['x']): (pos['x'] - first_pos['x'] + pos['w']), :] = item.rawImage
        self.app.logger.info(f"*tile_merge_end frame: {self.frame_id} group: {self.groupId}")

        if write_disk:
            video_name = pathlib.Path(self.app.get_video_property().video_name).stem
            save_path = pathlib.Path(self.app.config['server']['cache']['img_path']) / "{1}_{0}_{2}.jpg".format(
                self.frame_id, video_name, self.groupId)
            cv2.imwrite(str(save_path), self.raw_img)
            self.app.logger.info("save image: {}".format(save_path))

    def wait_for_detect(self):
        self.app.model.detect_cache.put({'frame_id': self.frame_id, 'img': [0], 'group_id': self.groupId, 'rect': self.rect, 'level': 'group'}) 

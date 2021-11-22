#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Friday, November 29th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import re
import numpy as np

import matplotlib.pyplot as plt
import pathlib
import yaml
import yamlordereddictloader
from utils.utils import str_to_mstimestamp
import numpy as np
import math

def avg_encoder_time(video_data):
    encoder_times = []
    for k, v in video_data.items():
        if 'feed_time' in v and v['feed_time']:
            feed_time = str_to_mstimestamp(v['feed_time'])
            tiles_send_time = []
            tile_id = 0
            while True:
                if 'Tile ' + str(tile_id) in v:
                    tile_data = v['Tile ' + str(tile_id)]
                    if 'tile_send_start_time' in tile_data:
                        tiles_send_time.append(str_to_mstimestamp(tile_data['tile_send_start_time']))
                else:
                    break
                tile_id += 1
            if len(tiles_send_time):
                encoder_times.append((k, max(tiles_send_time) - feed_time))
    # print(encoder_times)
    avg_time =np.mean(np.array([item[1] for item in encoder_times]))
    print(f"average encode time is: {avg_time}")

def avg_network_time(video_data):
    network_times = []
    for k, v in video_data.items():
        tile_id = 0
        tiles_start_time = []
        tiles_end_time = []
        while True:
            if 'Tile ' + str(tile_id) in v:
                tile_data = v['Tile ' + str(tile_id)]
                if 'tile_send_start_time' in tile_data and 'tile_recv_end_time' in tile_data:
                   tiles_start_time.append(str_to_mstimestamp(tile_data['tile_send_start_time']))
                   tiles_end_time.append(str_to_mstimestamp(tile_data['tile_recv_end_time']))
            else:
                break
            tile_id += 1
        if len(tiles_start_time) and len(tiles_end_time):
            network_times.append((k, max(tiles_end_time) - min(tiles_start_time)))
    # print(encoder_times)
    avg_time =np.mean(np.array([item[1] for item in network_times]))
    print(f"average network time is: {avg_time}") 

def average_tracker_time(video_data):
    tracker_times = []
    for k, v in video_data.items():
        if 'bbox_track_start_time' in v and 'bbox_track_end_time' in v:
            if v['bbox_track_start_time'] and v['bbox_track_end_time']:
                tracker_times.append(str_to_mstimestamp(v['bbox_track_end_time']) - str_to_mstimestamp(v['bbox_track_start_time']))
    avg_time = np.mean(np.array(tracker_times))

    print(f"average tracker time is: {avg_time}")

def average_infer_time(video_data):
    infer_times = []
    for k, v in video_data.items():
        if 'bbox_infer_start_time' in v and 'bbox_infer_end_time' in v:
            if v['bbox_infer_start_time'] and v['bbox_infer_end_time']:
                infer_times.append(str_to_mstimestamp(v['bbox_infer_end_time']) - str_to_mstimestamp(v['bbox_infer_start_time']))
    
    avg_time = np.mean(np.array(infer_times))

    print(f"average infer time is: {avg_time}")

def average_keyframe_time(video_data):
    keyframe_times = []
    for k, v in video_data.items():
        if 'feed_time' in v and 'bbox_recv_time' in v:
            if v['feed_time'] and v['bbox_recv_time']:
                keyframe_times.append(str_to_mstimestamp(v['bbox_recv_time']) - str_to_mstimestamp(v['feed_time']))
    avg_time = np.mean(np.array(keyframe_times))

    print(f"average total key frame time is: {avg_time}")

def average_mergeframe_time(video_data):
    merge_times = []
    for k, v in video_data.items():
        if 'tile_merge_start_time' in v and 'tile_merge_end_time' in v:
            if v['tile_merge_start_time'] and v['tile_merge_end_time']:
                merge_times.append(str_to_mstimestamp(v['tile_merge_end_time']) - str_to_mstimestamp(v['tile_merge_start_time']))
    avg_time = np.mean(np.array(merge_times))
    print(f"average merge time is :{avg_time}")

def average_transmission_time(video_data):
    network_times = []
    for k, v in video_data.items():
        tile_id = 0
        tiles_transmisssion_time = []
        while True:
            if 'Tile ' + str(tile_id) in v:
                tile_data = v['Tile ' + str(tile_id)]
                if 'tile_recv_start_time' in tile_data and 'tile_recv_end_time' in tile_data:
                   tiles_transmisssion_time.append(str_to_mstimestamp(tile_data['tile_recv_end_time']) - str_to_mstimestamp(tile_data['tile_recv_start_time']))       
            else:
                break
            tile_id += 1
        if len(tiles_transmisssion_time):
            network_times.append((k, sum(tiles_transmisssion_time)))
    # print(encoder_times)
    avg_time =np.mean(np.array([item[1] for item in network_times]))
    print(f"average transmission time is: {avg_time}") 

def average_decode_time(video_data):
    network_times = []
    for k, v in video_data.items():
        tile_id = 0
        tiles_decode_time = []

        while True:
            if 'Tile ' + str(tile_id) in v:
                tile_data = v['Tile ' + str(tile_id)]
                if 'tile_decode_time' in tile_data and 'tile_recv_end_time' in tile_data:
                   tiles_decode_time.append(str_to_mstimestamp(tile_data['tile_decode_time']) - str_to_mstimestamp(tile_data['tile_recv_end_time']))
            else:
                break
            tile_id += 1
        if len(tiles_decode_time):
            network_times.append((k, sum(tiles_decode_time)))
    avg_time = np.mean(np.array([item[1] for item in network_times]))
    print(f"average decode time is {avg_time}")

def test_1():
    video_name = 'ILSVRC2015_val_00000000'
    exp_name = 'tile3x3_ultrafast'
    date = '2019_12_06'
    dst_dir = pathlib.Path('data/exps/') / (video_name + '_' + exp_name + '_' + date)
    video_log = yaml.load(open(str(dst_dir / (video_name + '.yaml')), 'r'), Loader=yamlordereddictloader.Loader)
    avg_encoder_time(video_log)
    avg_network_time(video_log)
    average_transmission_time(video_log)
    average_tracker_time(video_log)
    average_infer_time(video_log)
    average_keyframe_time(video_log)
    average_decode_time(video_log)


if __name__ == '__main__':
    test_1()
    
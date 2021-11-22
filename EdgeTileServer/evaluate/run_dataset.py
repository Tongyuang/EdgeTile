#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Friday, December 6th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from config.load_config import global_config
import pathlib
import os
import time
import requests

video_dir = pathlib.Path(global_config['client']['dataset']['video'])
videos = video_dir.glob("*.mp4")
for v in videos:
    print(v)
    exit(0)
    # v = "data/ILSVRC_sample/video/ILSVRC2015_val_00000000.mp4"
    while True:
        r = requests.get("http://166.111.80.127:9002/status")
        response = r.json()
        if response['status'] == 1:
            break
        else:
            time.sleep(1)

    requests.get("http://166.111.80.127:9002/start")
    print(v)
    time.sleep(2)
    os.system(f"python edge_tile_client.py {str(v)}")
    
    # time.sleep(10)

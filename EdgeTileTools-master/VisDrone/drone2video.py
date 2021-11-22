#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Tuesday, February 18th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from pathlib import Path
import os
import imagesize

drone_root = Path("/Users/wangxu/Downloads/VisDrone2019-MOT-train/")
video_root = Path('/Users/wangxu/Git/EdgeTile-Client/data/drone/')

resolution = ['540p', '720p', '1080p', '2k']
resolution_size = [[960, 540], [1280, 720], [1920, 1080], [2560, 1440]]

for rid, resol in enumerate(resolution):
    seq_dir = drone_root / "sequences"
    seqs = [x for x in seq_dir.iterdir() if x.is_dir()]
    
    for seq in seqs:
        first_img = seq / '0000001.jpg'
        orig_width, orig_height = imagesize.get(str(first_img))
        if orig_height < 1440:
            continue
        video_path = video_root / ('video_' + resol)
        if not os.path.exists(video_path):
            video_path.mkdir(parents=True, exist_ok=True)
        cmd = "ffmpeg -r 30 -i " + str(seq) + "/%07d.jpg  -filter:v scale=-1:" + str(resolution_size[rid][1]) +" -c:v libx264  " + str(video_path / (seq.name + ".mp4"))
        os.system(cmd)
        print(seq)
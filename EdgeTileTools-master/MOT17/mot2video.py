#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, March 23rd 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from pathlib import Path
import os

mot_root = Path("/Users/wangxu/Edge/EdgeTileClient/data/mot17/raw/MOT17/train/")
video_root = Path('/Users/wangxu/Git/EdgeTile-Client/data/mot17/video')

for seq in mot_root.glob("**/*FRCNN/img1/"):
    print(seq)
    cmd = "ffmpeg -r 30 -i " + str(seq) + "/%06d.jpg -c:v libx264 " + str(video_root / (seq.parts[10] + ".mp4"))
    os.system(cmd)
    
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, July 13th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
group = ['4g_211', '4g_clou', '4g_redflag', '5g', '24g']

for gr in group:
    for i in range(3):
        g1 = gr + '_' + str(i + 1)
        file_path = f'/Users/wangxu/Edge/EdgeTileClient/data/drone/track/network_test/{g1}/{g1}.yaml'
         
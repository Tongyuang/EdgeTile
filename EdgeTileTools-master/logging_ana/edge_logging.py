#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, November 21st 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import datetime
import pathlib
import shutil
import os
from abc import abstractmethod
import re
from datetime import datetime
import yaml
import yamlordereddictloader
from collections import OrderedDict

from video_parser import VideoParser

class EdgeLogger:
    def __init__(self, video_name, exp_name):
        super().__init__()
        self.video_name = video_name
        self.exp_name = exp_name
    
    def load_encoder_or_decoder_log(self, filePath):
        f = open(filePath, 'r')
        records = list()
        for line in f.readlines():
            log_line = dict()
            r1 = re.compile("(([a-z_]+)\s((([a-z_]+):\s(-?\d+)\s?)+))")
            item = r1.findall(line)[0]
            log_type = item[1]
            log_line['type'] = log_type
            r2 = re.compile("([a-z_]+):\s(-?\d+)")
            pairs = r2.findall(item[2])
            for pair in pairs:
                log_line[pair[0]] = int(pair[1])
            records.append(log_line)
        return records
    
    def load_client_or_server_log(self, filePath):
        f = open(filePath, 'r')
        log_time_re = re.compile("^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})")
        mark_re = re.compile('\*(.*)')
        num_re = re.compile('^-?\d+$')
        records = list()
        upload_frames = set()
        for line in f.readlines():
            mark_data = mark_re.findall(line)
            if len(mark_data) > 0:
                record_time = log_time_re.findall(line)
                t = datetime.strptime(record_time[0], "%Y-%m-%d %H:%M:%S,%f")
                t1 = datetime.timestamp(t) * 1000
                r1 = re.compile("(([a-z_]+)\s((([a-z_]+):\s(-?\w+)\s?)+))")
                item = r1.findall(mark_data[0])
                if len(item) == 0:
                    print("come here")
                    r1 = re.compile("(([a-z_]+)\s(\d+))")
                    item = r1.findall(mark_data[0])
                    item = item[0]
                    
                    log_line = dict()
                    log_type = item[1]
                    log_line['type'] = log_type
                    log_line['frame'] = int(item[2])
                    log_line["time"] = t1
                    if log_line['frame'] not in upload_frames:
                        records.append(log_line)
                        upload_frames.add(log_line['frame'])
                else:
                    item = item[0]
                    log_line = dict()
                    log_type = item[1]
                    log_line['type'] = log_type
                    r2 = re.compile("([a-z_]+):\s(-?\w+)")
                    pairs = r2.findall(item[2])
                    for pair in pairs:
                        if len(num_re.findall(pair[1])) > 0:
                            log_line[pair[0]] = int(pair[1])
                        else:
                            log_line[pair[0]] = pair[1]
                    log_line["time"] = t1
                    records.append(log_line)

        return records
    
    def parse_logs(self):
        dst_dir = pathlib.Path('/Users/wangxu/Edge/EdgeTileClient/data/drone/track/network_test') / self.exp_name
        log1 = self.load_client_or_server_log(str(dst_dir / 'EdgeTileClient.log'))
        # log2 = self.load_client_or_server_log(str(dst_dir / 'EdgeTileServer.log'))
        # log3 = self.load_encoder_or_decoder_log(str(dst_dir / 'encoder.log'))
        # log4 = self.load_encoder_or_decoder_log(str(dst_dir / 'decoder.log'))
        v = VideoParser()
        v.parse(log1)
        # v.parse(log2)
        # v.parse(log3)
        # v.parse(log4)

        yaml.dump(v.dump(), open(str(dst_dir / (self.video_name + '.yaml')), 'w+'), Dumper=yamlordereddictloader.Dumper, default_flow_style=False)
        
if __name__ == "__main__":
    edge_logger = EdgeLogger("desktop", "desktop")
   
    # edge_logger.load_client_or_server_log("data/exps/ILSVRC2015_val_00000000_tile3x3_2019_11_30/client.log")
    edge_logger.parse_logs()
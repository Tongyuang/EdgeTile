#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, November 28th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import time
import numpy as np
import re
from config.load_config import global_config
from scipy.io import loadmat
import pathlib

class TimeEvaluator:
    def __init__(self, component, evaluator_name):
        super().__init__()
        self.time_samples = list()
        self.start_time = None
        self.end_time = None
        self.logger = component.logger
        self.evaluator_name = evaluator_name
        self.component = component
        self.component.app.manager.add(self)

    def tic(self):
        self.start_time = time.time()
    
    def toc(self):
        self.end_time = time.time()
        if self.start_time == None:
            self.logger.error(f"{self.evaluator_name}: You must tic before toc")
        else:
            self.time_samples.append(self.end_time - self.start_time)
    
    def avg_time(self):
        x = np.array(self.time_samples)
        avg = x.mean()
        self.component.logger.info(f"{self.evaluator_name}: average time: {avg} seconds.")
        return avg

class PerformanceEvaluator:
    def __init__(self, val_list_file, class_list_file, label_list_file):
        self.image_idx_map = dict()
        self.idx_image_map = dict()
        self.classname_idx_map = dict()
        self.idx_classname_map = dict()
        self.classcode_idx_map = dict()
        self.idx_classcode_map = dict()
        self.idx_label = dict()
        self.load_val_map(val_list_file)
        self.load_class_name(class_list_file)
        self.load_labels(label_list_file)

    def load_val_map(self, val_file):
        with open(val_file, 'r') as f:
            p = re.compile('(\S+) (\d+)')
            for line in f.readlines():   
                x = p.findall(line)
                if len(x) == 1:
                    self.image_idx_map[x[0][0]] = int(x[0][1])
                    self.idx_image_map[int(x[0][1])] = x[0][0]
    
    def load_class_name(self, class_file):
        f = open(class_file, 'r')
        for l in f.readlines():
            x = re.findall("(\w+) (\d+) (\w+)", l)
            if len(x) == 1:
                class_code = x[0][0]
                class_idx = int(x[0][1])
                class_name = x[0][2]
                self.classcode_idx_map[class_code] = class_idx
                self.idx_classcode_map[class_idx] = class_code
                self.classname_idx_map[class_name] = class_idx
                self.idx_classname_map[class_idx] = class_name
    
    def load_labels(self, label_file):
        f = open(label_file, 'r')
        idx = 1
        for l in f.readlines():
            x = re.findall("\d+", l)
            if len(x) > 0:
                self.idx_label[idx] = [int(k) for k in x]
            idx += 1
    
    def generate_predict_file(self, frame_property_list, output_file, blacklist_file):
        outputFile = open(output_file, 'w+')
        blacklistFile = open(blacklist_file, 'w+')
        for f in frame_property_list:
            frame_name = pathlib.Path(f.video_path).stem + '/{:06d}'.format(f.frame_idx)
            img_idx = self.image_idx_map[frame_name]
            if f.in_blacklist:
                for class_idx in self.idx_label[img_idx]:
                    blacklistFile.write(f"{img_idx} {self.idx_classcode_map[class_idx]}\n")
            else:
                for bbox in f.client_bbox:
                    outputFile.write(f"{img_idx} {self.classname_idx_map[bbox.class_name]} {bbox.confidence:.2f} {bbox.xmin:.2f} {bbox.ymin:.2f} {bbox.xmax:.2f} {bbox.ymax:.2f}\n")
                    
        
    
class TimeEvaluatorManager:
    def __init__(self):
        super().__init__()
        self.evaluators = list()

    def add(self, evaluator):
        self.evaluators.append(evaluator)

    def evaluate(self):
        for e in self.evaluators:
            e.avg_time()

if __name__ == "__main__":
    evaluator = PerformanceEvaluator(global_config['client']['dataset']['validate_set'], global_config['client']['dataset']['class_list'])
    print(f"{len(evaluator.image_idx.keys())}")
    

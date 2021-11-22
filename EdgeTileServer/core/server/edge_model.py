#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, November 27th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from core.edge_queue import EdgeQueue
from core.edge_component import EdgeComponent
from core.models.fake_detection import FakeDetection
# from core.models.detectron_detection import DetectronDetection
# from core.models.ultra_yolov3 import UltralyticsYolo
from utils.stoppable_thread import StoppableThread
from torch.multiprocessing import Process
from multiprocessing import  Queue
import pathlib
from threading import Thread
import time
import os
from concurrent.futures import ThreadPoolExecutor
from config.load_config import load_config
from os.path import join, getsize
import xml.etree.ElementTree as ET
from core.bbox_object import BBoxObject
def detect_func(logger, frame_obj, model, app, server_boxes):
    t1 = time.time()*1000
    logger.info(f"*bbox_infer_start frame: {frame_obj['frame_id']} level: group {frame_obj['group_id']}")
    dets = model.detect(frame_obj, server_boxes)
    logger.info(f"*bbox_infer_end frame: {frame_obj['frame_id']} level: group {frame_obj['group_id']}")
    dets['level'] = 'group'

    dets['group_id'] = frame_obj['group_id']
    dets['pid'] = 0
    app.socket.put_data(dets)
    t2 = time.time()*1000
    with open("/root/EdgeTileServer/data/log/detect_latency.txt", 'a', encoding='utf-8') as f:
        f.write("{} {} {}\n".format(frame_obj['frame_id'],  frame_obj['group_id'], t2-t1))
    print("*time_cost frame_id:{} group_id:{} infer_time:{}".format(frame_obj['frame_id'], frame_obj['group_id'], t2-t1))

class EdgeDets(StoppableThread):
    def __init__(self, model, q):
        super().__init__()
        self.q = q
        self.model = model

    def run(self):
        while not self.stopped():
            d = self.q.get()
            self.model.recv_dets(d)

# 多线程模式
class EdgeDetModel(StoppableThread):
    def __init__(self, parent,  q, pid):
        super().__init__()
        model = FakeDetection(id)
        self.model = model
        self.parent = parent
        self.q = q
        self.pid = pid

    def run(self):
        print(f"Start detect process {id}...")
        while not self.stopped():
            d = self.q.get()
            dets = self.model.detect(d)
            dets['pid'] = self.pid
            self.parent.recv_dets(dets)

# 多进程模式
def run_process(model_name, input_q, output_q, id):
    print(f"Start detect process {id}...")
    model = None
    if model_name == 'detectron_detection':
        # model = DetectronDetection(id)
        pass
    elif model_name == 'ultralytics_detection':
        # model = UltralyticsYolo(id)
        pass
    elif model_name == 'fake_detection':
        
        model = FakeDetection(id)
        pass
    while True:
        frame_obj = input_q.get()
        if frame_obj['frame_id'] == -1:
            print(f"Exit detect process {id}...")
            break
        dets = model.detect(frame_obj)
        dets['level'] = 'group'
        dets['group_id'] = frame_obj['group_id']
        dets['pid'] = id
        output_q.put(dets)


class EdgeModel(EdgeComponent):
    def __init__(self, app):
        super().__init__(app, 'model')
        
    
    def _initialize(self):
        select_model = self.config['select_model']
        pool_size = self.config['pool_size']
        self.model = FakeDetection(0)
        self.detect_cache = EdgeQueue(self, 'detect_cache')
        self.process_list = []
        self.q_list = []
        self.out_q = Queue()
        self.edge_dets = EdgeDets(self, self.out_q)
        self.server_boxes = {}
        
        # for i in range(pool_size):
        #     q = Queue()
        #     # q = EdgeQueue(self.app, 'default')
        #     # video_name = pathlib.Path(self.app.get_video_property().video_name).stem
        #     # p = Process(target=run_process,args=(select_model, q, self.out_q, i,))
        #     p = EdgeDetModel(self, q, i)
        #     self.q_list.append(q)
        #     self.process_list.append({'p': p, 'status': 0})
    
    def recv_dets(self, dets):
        pid = dets['pid']
        self.process_list[pid]['status'] = 0
        self.app.socket.put_data(dets)
    def load_boxes(self):
        anno_path = self.config['fake_detection']['anno']
        for root, dirs, files in os.walk(anno_path):
            files_num = len(files)
            for name in files:
                if len(name.split('.')) != 2:
                    continue
                frame_id = int(name.split('.xml')[0])
                frame_anno_path = join(root, name)
                self.server_boxes[frame_id] = []
                tree = ET.parse(frame_anno_path)
                for item in tree.findall(".//object"):
                    bbox_item = BBoxObject()
                    bbox_item.class_name = item.find("./name").text
                    bbox_item.track_id = int(item.find("./trackid").text)
                    bbox_item.xmax = float(item.find(".//xmax").text)
                    bbox_item.xmin = float(item.find(".//xmin").text)
                    bbox_item.ymax = float(item.find(".//ymax").text)
                    bbox_item.ymin = float(item.find(".//ymin").text)
                    bbox_item.confidence = 1.0
                    self.server_boxes[frame_id].append(bbox_item)
        print('load {} frames\' boxes finished!'.format(len(self.server_boxes.keys())))

    def run(self):
        # pool = ThreadPoolExecutor(max_workers=2)
        for p in self.process_list:
            p['p'].start()
        self.edge_dets.start()
        if os.path.exists("/root/EdgeTileServer/data/log/detect_latency.txt"):
            os.remove("/root/EdgeTileServer/data/log/detect_latency.txt")
        self.load_boxes()
        while not self.stopped():
            frame_obj = self.detect_cache.get()
            print("xxx get frame")
            if frame_obj['frame_id'] == -1:
                self.logger.info("edge model thread exit...")
                self.app.socket.put_data({'frame_id': -1})
                # self.edge_dets.stop()
                for q in self.q_list:
                    q.put(frame_obj)
                break
            else:
                video_name = pathlib.Path(self.app.get_video_property().video_name).stem
                frame_obj['video_name'] = video_name
                # pool.submit(detect_func, self.logger,frame_obj,self.model,self.app)
                t = Thread(target=detect_func, args=(self.logger,frame_obj,self.model,self.app,self.server_boxes))
                t.start()
                # select free process
                # selected_pid = -1
                # for i, p in enumerate(self.process_list):
                #     if p['status'] == 0:
                #         selected_pid = i
                #         break
                # if selected_pid >= 0:
                #    p['status'] = 1
                #     self.q_list[selected_pid].put(frame_obj)
                

#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, April 2nd 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from detectron2.config import get_cfg
import argparse
from detectron2.data.detection_utils import read_image
from detectron2.utils.logger import setup_logger
from detectron2.engine.defaults import DefaultPredictor
from core.models.model import Model
from core.frame import Frame as UploadFrame
from config.load_config import load_config
import pathlib
import time 
import numpy as np
import os
import torch
import pickle
from pathlib import Path
import cv2
from matplotlib import pyplot as plt
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
from xml.dom import minidom
from core.bbox_object import BBoxObject
from core.models.ultra_yolov3 import UltralyticsYolo, calculate_iou


class DetectronDetection:
    def __init__(self, pid):
        #super().__init__(app, "detectron_detection")
        config = load_config()
        self.config = config['server']['model']['detectron_detection']
        self.predictor = None
        self.pid = pid
        self._initialize()
    
    def _initialize(self):
        cfg = self.setup_cfg()
        torch.cuda.set_device(self.pid % 2) 
        self.predictor = DefaultPredictor(cfg)
        _ = self.predictor(np.zeros((512, 512, 3), dtype=np.uint8))

    def setup_cfg(self):
        # load config from file and command-line arguments
        cfg = get_cfg()
        cfg.merge_from_file(self.config["cfg_file"])
        cfg.merge_from_list(["MODEL.WEIGHTS", self.config["model_weight"]])
        # Set score_threshold for builtin models
        cfg.MODEL.RETINANET.SCORE_THRESH_TEST = self.config["confidence_threshold"]
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.config["confidence_threshold"]
        cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = self.config["confidence_threshold"]
        cfg.freeze()
        return cfg
    
    def detect(self, frame_obj):
        start_time = time.time()
        frame_id = frame_obj['frame_id']
        img = frame_obj['img']
        img = img.astype(np.uint8)
        predictions = self.predictor(img)
        # print(predictions)
        bboxes = predictions['instances'].get('pred_boxes').tensor.cpu().numpy()
        classes = predictions['instances'].get('pred_classes').cpu().numpy()
        scores = predictions['instances'].get('scores').cpu().numpy()
        boxes = dict()
        boxes['frame_id'] = frame_id 
        boxes['boxes'] = []
        class_list = {}
        class_list[0] = 'pedestrian'
        class_list[2] = 'car'
        group_x = 0
        group_y = 0
        if frame_obj['level'] == 'group':
            group_x = frame_obj['rect'][0]
            group_y = frame_obj['rect'][1]
        for i in range(bboxes.shape[0]):
            if classes[i] in [0, 2]:
                bb = bboxes[i]
                boxes['boxes'].append({'xmin': float(bb[0] + group_x), 'ymin': float(bb[1]+group_y), 'xmax': float(bb[2]+group_x), 
                    'ymax': float(bb[3]+group_y), 'class_name': class_list[classes[i]], 'confidence': float(scores[i]), 'track_id': int(-1)})
        end_time = time.time()
        print(f"detect cost time: {(end_time - start_time) * 1000} ms")
        return boxes

if __name__ == '__main__':
    u = DetectronDetection(1)
    # resolution = ['540p', '720p', '1080p', '2k']
    # resolution_size = [[960, 540], [1280, 720], [1920, 1080], [2560, 1440]]
    resolution = ['2k']
    resolution_size = [[2560, 1440]]
    
    for rid, resol in enumerate(resolution):
        video_root = Path('data/drone/video_' + resol + '_120fps') 
        for video_file in video_root.glob("**/*.mp4"):
            print(video_file.stem)
            if str(video_file.stem)  not in ['uav0000138_00000_v']:
                continue
            video_path = str(video_file)
            anno_path = 'data/drone/anno_' + resol + '_120fps/' + video_file.stem
            cap = cv2.VideoCapture(video_path)
            width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # float
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_idx = 0
            total_tp_car = 0
            total_pred_car = 0
            total_gt_car = 0
            total_tp_person = 0
            total_pred_person = 0
            total_gt_person = 0

            cmap = plt.get_cmap("tab10")
            color_list = [cmap(i) for i in np.linspace(0, 1, 10)]
            for i, c in enumerate(color_list):
                color_list[i] = (c[2] * 255, c[1] * 255, c[0] * 255)

            while(True):
            # Capture frame-by-frame
                ret, frame = cap.read()
                if frame is None:
                    break
                # img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = frame
                f = {'frame_id':frame_idx, 'img': img, 'level': 'frame'}
                bs = u.detect(f)
                pred_boxes = bs['boxes']
                # # split to 4 tile
                # split_width = 2
                # split_height = 2
                # split_x = [int(x) for x in np.linspace(0, img.shape[0], split_width + 1)]
                # split_y = [int(y) for y in np.linspace(0, img.shape[1], split_height + 1)]
                # pred_boxes = []
                # for k in range(split_width):
                #     for j in range(split_height):
                #         sub_img = img[split_x[k]: split_x[k + 1], split_y[j]: split_y[j + 1], :]
                #         f = {'frame_id':frame_idx, 'img': sub_img, 'level': 'group', 'rect': [split_y[j], split_x[k]]}
                #         bs = u.detect(f)
                #         pred_boxes += bs['boxes']
                        # raw_img = np.array(img, copy=True)
                        # for pred_box in pred_boxes:
                        #     cv2.rectangle(raw_img, (int(pred_box['xmin']), int(pred_box['ymin'])), (int(pred_box['xmax']), int(pred_box['ymax'])), color_list[3], 2)
                        # cv2.imwrite( "data/drone/pred/{:06d}.jpg".format(frame_idx), raw_img)
                tree = ET.parse(Path(anno_path) / '{:06d}.xml'.format(frame_idx)) 
                gt_boxes = []
                for item in tree.findall(".//object"):
                    class_name = item.find("./name").text
                    # class_name = {'pedestrian':'people', 'car':'car'}[class_name]
                    track_id = int(item.find("./trackid").text)
                    xmax = float(item.find(".//xmax").text)
                    xmin = float(item.find(".//xmin").text)
                    ymax = float(item.find(".//ymax").text)
                    ymin = float(item.find(".//ymin").text)
                    gt_boxes.append({'xmax': xmax, 'xmin': xmin, 'ymax': ymax, 'ymin': ymin, 'track_id': track_id, 'class_name': class_name})
                # cv2.rectangle(img, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color_list[9], 2)
                tp_car, gt_car, pred_car, tp_person, gt_person, pred_person, iou_arr = calculate_iou(pred_boxes, gt_boxes, iou_thres=0.5) 
                # print(f"car percision: {tp_car / pred_car}, car recall: {tp_car /gt_car}, person percision: {tp_person / max(pred_person, 1)} recall: {tp_person / max(gt_person, 1)}")
                total_tp_car += tp_car
                total_tp_person += tp_person
                total_gt_car += gt_car
                total_gt_person += gt_person
                total_pred_car += pred_car
                total_pred_person += pred_person
                img2 = img.copy()
                for pred_box in pred_boxes:
                    cv2.rectangle(img, (int(pred_box['xmin']), int(pred_box['ymin'])), (int(pred_box['xmax']), int(pred_box['ymax'])), color_list[0], 4)
                for pred_box in gt_boxes:
                    cv2.rectangle(img2, (int(pred_box['xmin']), int(pred_box['ymin'])), (int(pred_box['xmax']), int(pred_box['ymax'])), color_list[8], 2) 
                
                filter_boxes = []
                for pb in pred_boxes:
                    keep_box = False
                    pbb = BBoxObject()
                    pbb.from_dict(pb)
                    for gb in gt_boxes:
                        gbb = BBoxObject()
                        gbb.from_dict(gb)
                        iou = pbb.calculate_iou(gbb)
                        if iou >= 0.3:
                            keep_box = True
                            break
                    if keep_box:
                        filter_boxes.append(pb)

                cv2.imwrite( "data/drone/pred/{:06d}_pred.jpg".format(frame_idx), img)
                cv2.imwrite( "data/drone/pred/{:06d}_gt.jpg".format(frame_idx), img2)
                # save_dir = Path("data/drone/server_box_" + resol + "_120fps/" + video_file.stem)
                # if not os.path.exists(save_dir):
                #     save_dir.mkdir(parents=True, exist_ok=True)
                # write_xml(str(save_dir / ("{:06d}.xml".format(frame_idx))), filter_boxes)
                frame_idx += 1
            pc = total_tp_car / total_pred_car
            rc = total_tp_car / total_gt_car
            pp = total_tp_person / total_pred_person
            rp = total_tp_person / total_gt_person
            print(f"car f1: {2 * pc * rc / (pc + rc), 2 * pp * rp / (pp + rp)} percision: {pc}, car recall: {rc}, person percision: {total_tp_person / total_pred_person} recall: {total_tp_person / total_gt_person}")
            
            

                

            # When everything done, releas the capture
            cap.release()
    

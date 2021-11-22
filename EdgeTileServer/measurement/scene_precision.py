#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, July 16th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from core.models.ultra_yolov3 import UltralyticsYolo, calculate_iou
from pathlib import Path
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
from xml.dom import minidom
from core.bbox_object import BBoxObject
import cv2
from utils.utils import *

def analyse_accuracy():
    u = UltralyticsYolo(1)
    # resolution = ['540p', '720p', '1080p', '2k']
    # resolution_size = [[960, 540], [1280, 720], [1920, 1080], [2560, 1440]]
    resolution = ['2k']
    resolution_size = [[2560, 1440]]
    
    for rid, resol in enumerate(resolution):
        video_root = Path('data/drone/video_' + resol) 
        for video_file in video_root.glob("**/*.mp4"):
            # video_path = str(video_file)
            video_path = 'data/drone/video_2k_120fps/uav0000138_00000_v.mp4'
            video_file = Path(video_path)
            print(video_path)
            anno_path = 'data/drone/yolov3_spp_anno_' + resol + '_120fps/' + video_file.stem
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
            total_iou = []

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
                total_iou += iou_arr
                # print(f"car percision: {tp_car / pred_car}, car recall: {tp_car /gt_car}, person percision: {tp_person / max(pred_person, 1)} recall: {tp_person / max(gt_person, 1)}")
                total_tp_car += tp_car
                total_tp_person += tp_person
                total_gt_car += gt_car
                total_gt_person += gt_person
                total_pred_car += pred_car
                total_pred_person += pred_person
                frame_idx += 1
                
                # for pred_box in pred_boxes:
                #     cv2.rectangle(img, (int(pred_box['xmin']), int(pred_box['ymin'])), (int(pred_box['xmax']), int(pred_box['ymax'])), color_list[3], 4)
                # for pred_box in gt_boxes:
                #     cv2.rectangle(img, (int(pred_box['xmin']), int(pred_box['ymin'])), (int(pred_box['xmax']), int(pred_box['ymax'])), color_list[4], 2) 
                
                
            pc = total_tp_car / total_pred_car
            rc = total_tp_car / total_gt_car
            pp = total_tp_person / total_pred_person
            rp = total_tp_person / total_gt_person
            
            accu = sum(total_iou) / len(total_iou) 
            print(f"accu: {accu} {(total_tp_car + total_tp_person) / (total_pred_car + total_pred_person)} {(total_tp_car + total_tp_person) / (total_gt_car + total_gt_person)} {pc} {rc} {total_tp_person / max(1, total_pred_person)} {total_tp_person / max(1, total_gt_person)}")
            

            # When everything done, releas the capture
            cap.release()
            break

if __name__ == '__main__':
    analyse_accuracy()

    
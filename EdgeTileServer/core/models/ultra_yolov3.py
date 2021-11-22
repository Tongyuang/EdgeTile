#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, April 16nd 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
import torch
from config.load_config import load_config
import sys
# sys.path.insert(0, '/home/edge/EdgeTile/libs/yolov3')
from libs.yolov3.models import *
from libs.yolov3.utils.datasets import *
from utils.utils import *
import numpy as np
import pickle
import cv2
import random
from pathlib import Path
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
from xml.dom import minidom
from core.bbox_object import BBoxObject


class UltralyticsYolo:
    def __init__(self, pid):
        super().__init__()
        self.pid = pid
        config = load_config()
        self.config = config['server']['model']['ultralytics_detection']
        self.device = None
        self.model = None
        self._initialize()
    
    def _initialize(self):
        self.img_size = self.config['img_size']
        self.weight_file = self.config['model_weight']
        self.cfg_file = self.config['cfg_file']
        self.name_file = self.config['name_file']
        self.conf_thres = self.config['conf_thres']
        self.iou_thres = self.config['iou_thres']
        # self.names = load_classes(self.name_file)
        # self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]
        # torch.cuda.set_device(self.pid % 2)
        self.device = torch_utils.select_device(device='0')
        self.model = Darknet(self.cfg_file, self.img_size)
        self.model.load_state_dict(torch.load(self.weight_file, map_location=self.device)['model'])
        # load_darknet_weights(self.model, self.weight_file)
        self.model.to(self.device).eval()
        # _ = self.model(torch.zeros((1, 3, self.img_size, self.img_size), device=self.device))
    
    def detect(self, frame_obj):
        start_time = time.time()
        img0 = frame_obj['img']
        frame_id = frame_obj['frame_id']
        img = letterbox(img0, new_shape=self.img_size)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.float() 
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        end_time1 = time.time()
        # print(f"preprocess time{end_time1 - start_time}")
        pred = self.model(img, augment=False)[0]
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres,
                                   multi_label=False, agnostic=True)
        det = pred[0]
        end_time2 = time.time()
        if det is not None and len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()
        # for *xyxy, conf, cls in det:
        #     label = '%s %.2f' % (self.names[int(cls)], conf)
        #     plot_one_box(xyxy, img0, label=label, color=self.colors[int(cls)])
        # cv2.imwrite('data/a.jpg', img0)
        # det = det.cpu().numpy()
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
        for *xyxy, conf, cls in det:
            if int(cls) in [0, 2]:
                bb = xyxy
                boxes['boxes'].append({'xmin': float(bb[0] + group_x), 'ymin': float(bb[1]+group_y), 'xmax': float(bb[2]+group_x), 
                    'ymax': float(bb[3]+group_y), 'class_name': class_list[int(cls)], 'confidence': float(conf), 'track_id': int(-1)})
        end_time = time.time()
        print(f"detect cost time: {(end_time1 - start_time) * 1000}ms  {(end_time2 - end_time1) * 1000}  {(end_time - end_time2) * 1000} ms")
        return boxes

def calculate_iou(pred_boxes, gt_boxes, iou_thres = 0.5):
    tp_car = 0
    tp_person = 0
    gt_car_count = 0
    gt_person_count = 0
    pred_car_count = 0
    pred_person_count = 0
    filter_pred_cars = [b for b in pred_boxes if b['class_name'] == 'car']
    pred_car_count = len(filter_pred_cars)
    filter_gt_cars = [b for b in gt_boxes if b['class_name'] == 'car']
    gt_car_count = len(filter_gt_cars)
    filter_pred_person = [b for b in pred_boxes if b['class_name'] == 'pedestrian']
    pred_person_count = len(filter_pred_person)
    filter_gt_person = [b for b in gt_boxes if b['class_name'] == 'pedestrian']
    gt_person_count = len(filter_gt_person)
    filter_pred_cars_arr = [[b['xmin'], b['ymin'], b['xmax'], b['ymax']] for b in filter_pred_cars]
    filter_pred_person_arr = [[b['xmin'], b['ymin'], b['xmax'], b['ymax']] for b in filter_pred_person]
    filter_pred_cars_arr = np.array(filter_pred_cars_arr)
    filter_pred_person_arr = np.array(filter_pred_person_arr)
    iou_array = []
    for gt_car in filter_gt_cars:
        if filter_pred_cars_arr.size > 0:
            ixmin = np.maximum(filter_pred_cars_arr[:, 0], gt_car['xmin'])
            iymin = np.maximum(filter_pred_cars_arr[:, 1], gt_car['ymin'])
            ixmax = np.minimum(filter_pred_cars_arr[:, 2], gt_car['xmax'])
            iymax = np.minimum(filter_pred_cars_arr[:, 3], gt_car['ymax'])
            iw = np.maximum(ixmax - ixmin + 1.0, 0.0)
            ih = np.maximum(iymax - iymin + 1.0, 0.0)
            inters = iw * ih

            # union
            uni = (
                (gt_car['xmax'] - gt_car['xmin'] + 1.0) * (gt_car['ymax'] - gt_car['ymin'] + 1.0)
                + (filter_pred_cars_arr[:, 2] - filter_pred_cars_arr[:, 0] + 1.0) * (filter_pred_cars_arr[:, 3] - filter_pred_cars_arr[:, 1] + 1.0)
                - inters
            )

            overlaps = inters / uni
            iou = np.max(overlaps)
            if iou > iou_thres:
                tp_car += 1
            iou_array.append(iou)
            
    for gt_person in filter_gt_person:
        if filter_pred_person_arr.size > 0:
            ixmin = np.maximum(filter_pred_person_arr[:, 0], gt_person['xmin'])
            iymin = np.maximum(filter_pred_person_arr[:, 1], gt_person['ymin'])
            ixmax = np.minimum(filter_pred_person_arr[:, 2], gt_person['xmax'])
            iymax = np.minimum(filter_pred_person_arr[:, 3], gt_person['ymax'])
            iw = np.maximum(ixmax - ixmin + 1.0, 0.0)
            ih = np.maximum(iymax - iymin + 1.0, 0.0)
            inters = iw * ih

            # union
            uni = (
                (gt_person['xmax'] - gt_person['xmin'] + 1.0) * (gt_person['ymax'] - gt_person['ymin'] + 1.0)
                + (filter_pred_person_arr[:, 2] - filter_pred_person_arr[:, 0] + 1.0) * (filter_pred_person_arr[:, 3] - filter_pred_person_arr[:, 1] + 1.0)
                - inters
            )

            overlaps = inters / uni
            iou = np.max(overlaps)
            if iou > iou_thres:
                tp_person += 1
            iou_array.append(iou)
    return tp_car, gt_car_count, pred_car_count, tp_person, gt_person_count, pred_person_count, iou_array
    
def write_xml(dst_file, json_content):
    anno = ET.Element('annotation')
    for obj in json_content:
        obj_ele = ET.SubElement(anno, 'object')
        track_id = ET.SubElement(obj_ele, 'trackid')
        track_id.text = str(obj['track_id'])
        name = ET.SubElement(obj_ele, 'name')
        name.text = str(obj['class_name'])
        bndbox = ET.SubElement(obj_ele, 'bndbox')
        xmin = ET.SubElement(bndbox, 'xmin')
        xmax = ET.SubElement(bndbox, 'xmax')
        ymin = ET.SubElement(bndbox, 'ymin')
        ymax = ET.SubElement(bndbox, 'ymax')
        xmin.text = str(obj['xmin'])
        ymin.text = str(obj['ymin'])
        xmax.text = str(obj['xmax'])
        ymax.text = str(obj['ymax'])

    mydata = ET.tostring(anno, 'utf-8')
    reparsed = minidom.parseString(mydata)
    mydata = reparsed.toprettyxml(indent="\t")
    myfile = open(dst_file, "w")
    myfile.write(mydata)

if __name__ == '__main__':
    u = UltralyticsYolo(1)
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
                # for pred_box in pred_boxes:
                #     cv2.rectangle(img, (int(pred_box['xmin']), int(pred_box['ymin'])), (int(pred_box['xmax']), int(pred_box['ymax'])), color_list[0], 4)
                # for pred_box in gt_boxes:
                #     cv2.rectangle(img2, (int(pred_box['xmin']), int(pred_box['ymin'])), (int(pred_box['xmax']), int(pred_box['ymax'])), color_list[8], 2) 
                
                # filter_boxes = []
                # for pb in pred_boxes:
                #     keep_box = False
                #     pbb = BBoxObject()
                #     pbb.from_dict(pb)
                #     for gb in gt_boxes:
                #         gbb = BBoxObject()
                #         gbb.from_dict(gb)
                #         iou = pbb.calculate_iou(gbb)
                #         if iou >= 0.3:
                #             keep_box = True
                #             break
                #     if keep_box:
                #         filter_boxes.append(pb)

                # cv2.imwrite( "data/drone/pred/{:06d}_pred.jpg".format(frame_idx), img)
                # cv2.imwrite( "data/drone/pred/{:06d}_gt.jpg".format(frame_idx), img2)
                save_dir = Path("data/drone/yolov3_spp_anno_" + resol + "_120fps/" + video_file.stem)
                if not os.path.exists(save_dir):
                    save_dir.mkdir(parents=True, exist_ok=True)
                write_xml(str(save_dir / ("{:06d}.xml".format(frame_idx))), pred_boxes)
                frame_idx += 1
            pc = total_tp_car / total_pred_car
            rc = total_tp_car / total_gt_car
            pp = total_tp_person / total_pred_person
            rp = total_tp_person / total_gt_person
            print(f"car f1: {2 * pc * rc / (pc + rc), 2 * pp * rp / (pp + rp)} percision: {pc}, car recall: {rc}, person percision: {total_tp_person / total_pred_person} recall: {total_tp_person / total_gt_person}")
            # When everything done, releas the capture
            cap.release()
    
        
        

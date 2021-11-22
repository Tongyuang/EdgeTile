#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, May 23rd 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
import torch
from siamrpn import TrackerSiamRPN, SiamRPN
from pathlib import Path
from matplotlib import pyplot as plt
import os
import numpy as np
import cv2
import xml.etree.ElementTree as ET
import time
from xml.dom import minidom

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

def load_gt(video_name, frame_id):
    anno_path = Path('/srv/node/sdd1/VisDrone2019-MOT-val/drone/anno_2k/')
    anno_path = anno_path / video_name
    tree = ET.parse(anno_path / '{:06d}.xml'.format(frame_id)) 
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
    return gt_boxes

def convert_video(video_name):
    video_file = Path('/srv/node/sdd1/VisDrone2019-MOT-val/drone/video_2k_120fps/') / f"{video_name}.mp4"
    output_dir = Path('/srv/node/sdd1/VisDrone2019-MOT-val/drone/video_2k_120fps/') / f"{video_name}_gt/"
    anno_dir = Path('/srv/node/sdd1/VisDrone2019-MOT-val/drone/anno_2k_120fps/') / video_name 
    if not os.path.exists(output_dir):
        os.mkdir(output_dir) 

    if not os.path.exists(anno_dir):
        os.mkdir(anno_dir) 

    frame_id = 0
    tracker_list = []
    net_dir = '/home/edge/EdgeTileTools/model.pth'
    net = SiamRPN()
    cuda = torch.cuda.is_available()
    device = torch.device('cuda:0' if cuda else 'cpu')
    if net_dir is not None:
        net.load_state_dict(torch.load(net_dir, map_location=lambda storage, loc: storage))
        net = net.to(device)

    gt_boxes = None
    cmap = plt.get_cmap("tab20b")
    color_list = [cmap(i) for i in np.linspace(0, 1, 20)]


    # rgb to bgr
    for i, c in enumerate(color_list):
        color_list[i] = (c[2] * 255, c[1] * 255, c[0] * 255)
    
    font_scale = 1.5
    font = cv2.FONT_HERSHEY_PLAIN
    cap = cv2.VideoCapture(str(video_file))
    
    while cap.isOpened():
        ret, frame = cap.read()

        if ret == True:
            print(frame_id)
            t1 = time.time()
            render_box = None
            update_frames = []
            for i in range(3):
                ret, uf = cap.read()
                update_frames.append(uf)
                if ret == False:
                    break
            
            if len(update_frames) > 0:
                gt_boxes = load_gt(video_name, int(frame_id))
                update_boxes = [[], [], []]
                for bid, bbox in enumerate(gt_boxes):
                    
                    rpn = TrackerSiamRPN(net, net_path=net_dir)
                    box = (bbox['xmin'], bbox['ymin'], bbox['xmax'] - bbox['xmin'], bbox['ymax'] - bbox['ymin'])
                    rpn.init(frame, box)
                    for ui, uf in enumerate(update_frames):
                        ret, box, _ = rpn.update(frame)
                        bbox = {'xmin': box[0], 'ymin': box[1], 'xmax': box[0] + box[2], 'ymax': box[1] + box[3], 'track_id': gt_boxes[bid]['track_id'], 'class_name': gt_boxes[bid]['class_name']}
                        update_boxes[ui].append(bbox)
            t2 = time.time()
            print(f"time cost: {t2 - t1} seconds")
            img = frame
            # for t in gt_boxes:
            #     cv2.rectangle(img, (int(t["xmin"]), int(t["ymin"])), (int(t["xmax"]), int(t["ymax"])), (255, 0, 0), 2)
                
            #     text = t["class_name"]
            #     (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=2)[0]
            #     cv2.rectangle(img, (int(t["xmin"]), int(t["ymin"])), (int(t["xmin"] + text_width), int(t["ymin"] + text_height)), color_list[0], cv2.FILLED)
            #     cv2.putText(img, text, (int(t["xmin"]), int(t["ymin"] + text_height)),  color=(255, 255, 255), fontFace=font, fontScale=font_scale)
            # cv2.imwrite(str(output_dir / '{:06d}.jpg'.format(frame_id * 4)),  img)

            
            
            dst_file = anno_dir / '{:06d}.xml'.format(frame_id * 4)
            write_xml(dst_file, gt_boxes)

            for ui, uf in enumerate(update_frames):
                # for t in update_boxes[ui]:
                #     cv2.rectangle(uf, (int(t["xmin"]), int(t["ymin"])), (int(t["xmax"]), int(t["ymax"])), (255, 0, 0), 2)
                    
                #     text = t["class_name"]
                #     (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=2)[0]
                #     cv2.rectangle(uf, (int(t["xmin"]), int(t["ymin"])), (int(t["xmin"] + text_width), int(t["ymin"] + text_height)), color_list[0], cv2.FILLED)
                #     cv2.putText(uf, text, (int(t["xmin"]), int(t["ymin"] + text_height)),  color=(255, 255, 255), fontFace=font, fontScale=font_scale)
                # cv2.imwrite(str(output_dir / '{:06d}.jpg'.format(frame_id * 4 + ui + 1)),  uf)
            
                dst_file = anno_dir / '{:06d}.xml'.format(frame_id * 4 + ui + 1)
                write_xml(dst_file, update_boxes[ui])
            frame_id += 1
        else:
            break
    cap.release()

if __name__ == '__main__':
    video_root = Path('/srv/node/sdd1/VisDrone2019-MOT-val/drone/video_2k_120fps/')
    for video_file in video_root.glob("**/*.mp4"):
        print(video_file.stem)
        convert_video(video_file.stem)

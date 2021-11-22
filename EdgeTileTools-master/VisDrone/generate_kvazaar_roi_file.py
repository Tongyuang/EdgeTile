#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Tuesday, July 21st 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from pathlib import Path
from core.frame import FrameProperty
from core.video_property import VideoProperty
import numpy as np
import struct
import cv2
from matplotlib import pyplot as plt

def estimate_roi(roi_file, frames, roi_width, roi_height):
    # estimate roi
    with open(str(roi_file), 'wb') as f:
        frame_id = 0

        for fp in frames:
            print(frame_id)
            frame_id += 1
            roi_area = np.zeros((roi_width, roi_height))
            for bbox in fp.bbox:
                x1 = max(0, int((bbox.xmin - 1) / 128))
                y1 = max(0, int((bbox.ymin - 1)  / 128))
                x2 = min(roi_width - 1, int((bbox.xmax - 1) / 128))
                y2 = min(roi_height - 1, int((bbox.ymax - 1) / 128))
                for m in range(x1, x2 + 1):
                    for n in range(y1, y2 + 1):
                        roi_area[m][n] = 1
            f.write(struct.pack('i', roi_width))
            f.write(struct.pack('i', roi_height))
            for i in range(roi_height):
                for j in range(roi_width):
                    if roi_area[j][i] == 1 or fp.frame_idx == 0:
                        # f.write('22 ')
                        f.write(struct.pack('b', 0))
                    else:
                        # f.write('0 ')
                        f.write(struct.pack('b', 22)) 
        
        # for fp in frames:
        #     print(frame_id)
        #     frame_id += 1
        #     roi_area = np.zeros((roi_width, roi_height))
        #     for bbox in fp.bbox:
        #         x1 = max(0, int((bbox.xmin - 1)/ 128))
        #         y1 = max(0, int((bbox.ymin - 1)  / 128))
        #         x2 = min(roi_width - 1, int((bbox.xmax - 1) / 128))
        #         y2 = min(roi_height - 1, int((bbox.ymax - 1) / 128))
        #         for m in range(x1, x2 + 1):
        #             for n in range(y1, y2 + 1):
        #                 roi_area[m][n] = 1
        #     f.write(struct.pack('i', roi_width))
        #     f.write(struct.pack('i', roi_height))
        #     for i in range(roi_height):
        #         for j in range(roi_width):
        #             if roi_area[j][i] == 0:
        #                 # f.write('22 ')
        #                 f.write(struct.pack('b', 22))
        #             else:
        #                 # f.write('0 ')
        #                 f.write(struct.pack('b', 0)) 
        
        f.close()

def estimate_roi_txt(roi_file, frames, roi_width, roi_height):
    # estimate roi
    with open(str(roi_file), 'w', encoding='utf-8') as f:
        frame_id = 0
        for fp in frames:
            print(frame_id)
            frame_id += 1
            roi_area = np.zeros((roi_width, roi_height))
            for bbox in fp.bbox:
                x1 = max(0, int((bbox.xmin - 1) / 128))
                y1 = max(0, int((bbox.ymin - 1)  / 128))
                x2 = min(roi_width - 1, int((bbox.xmax - 1) / 128))
                y2 = min(roi_height - 1, int((bbox.ymax - 1) / 128))
                for m in range(x1, x2 + 1):
                    for n in range(y1, y2 + 1):
                        roi_area[m][n] = 1
            f.write("{},{},{}\n".format(fp.frame_idx, roi_width, roi_height))
            
            for i in range(roi_height):
                for j in range(roi_width):
                    if roi_area[j][i] == 1 or fp.frame_idx == 0:
                        f.write('0 ')
                    else:
                        f.write('22 ')
                f.write('\n')
        
        f.close()

def estimate_upload_order(upload_order_file, frames, tile_width, tile_height):
    with open(str(upload_order_file), 'w', encoding='utf-8') as f:
        f2 = open("upload_order.txt", 'w', encoding='utf-8')
        for fp in frames:
            frame_id = fp.frame_idx
            tile_area = np.zeros((tile_width, tile_height))
            tile_min_width = fp.w / tile_width
            tile_min_height = fp.h / tile_height
            
            for bbox in fp.bbox:
                # 找到bbox的中心点所在的tile
                x = ((bbox.xmin+bbox.xmax)/2) / tile_min_width
                x = int(x)
                y = ((bbox.ymin+bbox.ymax)/2) / tile_min_height
                y = int(y)
                tile_area[x][y] += 1
            f2.write("{},{},{},{}\n".format(fp.frame_idx, tile_width, tile_height,len(fp.bbox)))
            
            f.write("{},".format(fp.frame_idx))
            total_num = 0
            object_nums = []
            for i in range(tile_height):
                for j in range(tile_width):
                    f2.write('{} '.format(int(tile_area[j][i])))
                    total_num += int(tile_area[j][i])
                    object_nums.append(tile_area[j][i])
                f2.write('\n')
            li = np.array(object_nums)
            upload_order = np.argsort(-li)
            for x in list(upload_order):
                f.write('{} '.format(int(x)))
                f2.write('{} '.format(int(x)))
            f.write('\n')
            f2.write('\n')
            # f.write('\ntotal:{}\n'.format(total_num))
        f.close()


if __name__ == "__main__":
    video_name = 'uav0000138_00000_v.mp4'
    video_width = 2560
    video_height = 1440
    video_path = '/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/video_2k_120fps/uav0000138_00000_v.mp4'
    local_detect = Path('/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/YOLOv3/uav0000138_00000_v/')
    server_detect = Path('/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/yolov3_spp_anno_2k_120fps/uav0000138_00000_v/')
    roi_file = Path('output/roi_files/EAAR/roi_file.txt')
    roi_txt_file = Path('output/roi_files/EAAR/roi.txt')
    upload_order_file = Path('output/roi_files/EAAR/upload_order_file.txt')
    max_frame_id = 848
    server_step = 24
    roi_width = 20
    roi_height = 12
    tile_width = 4
    tile_height = 3
    iou_thres = 0.3
    is_export_img = False
    if is_export_img:
        cap = cv2.VideoCapture(video_path)
        imgs = []
        while(True):
            # Capture frame-by-frame
            ret, frame = cap.read()
        
            if frame is None:
                break
            imgs.append(frame)
    cmap = plt.get_cmap("tab10")
    color_list = [cmap(i) for i in np.linspace(0, 1, 10)]
    for i, c in enumerate(color_list):
        color_list[i] = (c[2] * 255, c[1] * 255, c[0] * 255)
    frames = []
    for i in range(0, max_frame_id, server_step):
        fp = FrameProperty(video_path, i, 2560, 1440, server_step)
        fp.load_local_bbox(local_detect)
        fp.load_server_bbox(server_detect)
        if is_export_img:
            img = imgs[i]
        for sbox in fp.server_bbox:
            is_match = False
            for lbox in fp.client_bbox:
                iou = sbox.calculate_iou(lbox)
                if iou >= iou_thres:
                    is_match = True
                    break
            # is_match = False
            if not is_match:
                fp.bbox.append(sbox)
                if is_export_img:
                    cv2.rectangle(img, (int(sbox.xmin), int(sbox.ymin)), (int(sbox.xmax), int(sbox.ymax)), color_list[3], 4)
            # else:
            #     cv2.rectangle(img, (int(sbox.xmin), int(sbox.ymin)), (int(sbox.xmax), int(sbox.ymax)), color_list[0], 2)
        if is_export_img:
            # for sbox in fp.client_bbox:
            #     cv2.rectangle(img, (int(sbox.xmin), int(sbox.ymin)), (int(sbox.xmax), int(sbox.ymax)), color_list[6], 2)
            cv2.imwrite( "pred/{:06d}.jpg".format(i), img)
        frames.append(fp)

    video_property = VideoProperty(video_name, video_width, video_height, tile_width, tile_height)
    
    estimate_roi(roi_file, frames, roi_width, roi_height)
    # test generated roi
    estimate_roi_txt(roi_txt_file, frames, roi_width, roi_height)
    estimate_upload_order(upload_order_file, frames, tile_width, tile_height)
    print("finish!")






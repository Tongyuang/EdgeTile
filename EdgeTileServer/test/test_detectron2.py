#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, March 21st 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from detectron2.config import get_cfg
import argparse
from detectron2.data.detection_utils import read_image
from detectron2.utils.logger import setup_logger
from detectron2.engine.defaults import DefaultPredictor
from pathlib import Path
import numpy as np
import cv2

config_file = 'libs/detectron2/configs/COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml'
def setup_cfg(args):
    # load config from file and command-line arguments
    cfg = get_cfg()
    cfg.merge_from_file(config_file)
    cfg.merge_from_list(args.opts)
    # Set score_threshold for builtin models
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = args.confidence_threshold
    cfg.freeze()
    return cfg

def get_parser():
    parser = argparse.ArgumentParser(description="Detectron2 demo for builtin models")
    parser.add_argument(
        "--config-file",
        default=config_file,
        metavar="FILE",
        help="path to config file",
    )
    
    parser.add_argument(
        "--output",
        default= "data/rcnn/",
        help="A file or directory to save output visualizations. "
        "If not given, will show output in an OpenCV window.",
    )

    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.5,
        help="Minimum score for instance predictions to be shown",
    )
    parser.add_argument(
        "--opts",
        help="Modify config options using the command-line 'KEY VALUE' pairs",
        default=["MODEL.WEIGHTS", "data/models/model_final_68b088.pkl"],
        nargs=argparse.REMAINDER,
    )
    return parser

if __name__ == '__main__':
    print("hello world")
    args = get_parser().parse_args()
    cfg = setup_cfg(args)
    predictor = DefaultPredictor(cfg)
    imgs_dir = Path("/srv/node/sdd1/VisDrone2019-MOT-val/sequences/uav0000137_00458_v")
    class_name = 'pedestrian'
    pred_file = open(f'data/drone/{class_name}.txt', 'w')
    for img_path in imgs_dir.glob("**/*.jpg"):
        img_id = int(img_path.stem) - 1
        print(f"process img: {img_id}.\n")
        img = read_image(str(img_path), format="BGR")
        predictions = predictor(img)
        # print(predictions)
        bboxes = predictions['instances'].get('pred_boxes').tensor.cpu().numpy()
        classes = predictions['instances'].get('pred_classes').cpu().numpy()
        scores = predictions['instances'].get('scores').cpu().numpy()
        is_split = True
        if not is_split:
            for i in range(bboxes.shape[0]):
                if classes[i] == 0:
                    pred_file.write(f"{img_id} {scores[i]} {bboxes[i][0]} {bboxes[i][1]} {bboxes[i][2]} {bboxes[i][3]}\n") 
        else:
            split_width = 2
            split_height = 2
            split_x = [int(x) for x in np.linspace(0, img.shape[0], split_width + 1)]
            split_y = [int(y) for y in np.linspace(0, img.shape[1], split_height + 1)]
            filter_bboxes = []
            for i in range(bboxes.shape[0]):
                if classes[i] == 0 and ((bboxes[i][0] < split_y[1] and bboxes[i][2] > split_y[1]) or (bboxes[i][1] < split_x[1] and bboxes[i][3] > split_x[1])):
                    filter_bboxes.append(bboxes[i])
                    pred_file.write(f"{img_id} {scores[i]} {bboxes[i][0]} {bboxes[i][1]} {bboxes[i][2]} {bboxes[i][3]}\n")
            BBGT = np.array(filter_bboxes)
            for k in range(split_width):
                for j in range(split_height):
                    sub_img = img[split_x[k]: split_x[k + 1], split_y[j]: split_y[j + 1], :]
                    # sub_img = cv2.resize(sub_img, dsize=(img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)
                    predictions = predictor(sub_img)
                    # print(predictions)
                    bboxes = predictions['instances'].get('pred_boxes').tensor.cpu().numpy()
                    classes = predictions['instances'].get('pred_classes').cpu().numpy()
                    scores = predictions['instances'].get('scores').cpu().numpy()
                    for i in range(bboxes.shape[0]):
                        if classes[i] == 0:
                            bb = bboxes[i]
                            iou = 0
                            if BBGT.size > 0:
                                # compute overlaps
                                # intersection
                                ixmin = np.maximum(BBGT[:, 0], bb[0])
                                iymin = np.maximum(BBGT[:, 1], bb[1])
                                ixmax = np.minimum(BBGT[:, 2], bb[2])
                                iymax = np.minimum(BBGT[:, 3], bb[3])
                                iw = np.maximum(ixmax - ixmin + 1.0, 0.0)
                                ih = np.maximum(iymax - iymin + 1.0, 0.0)
                                inters = iw * ih

                                # union
                                uni = (
                                    (bb[2] - bb[0] + 1.0) * (bb[3] - bb[1] + 1.0)
                                    + (BBGT[:, 2] - BBGT[:, 0] + 1.0) * (BBGT[:, 3] - BBGT[:, 1] + 1.0)
                                    - inters
                                )

                                overlaps = inters / uni
                                iou = np.max(overlaps)
                            if iou < 0.5:
                                pred_file.write(f"{img_id} {scores[i]} {bboxes[i][0] + split_y[j]} {bboxes[i][1] + split_x[k]} {bboxes[i][2] + split_y[j]} {bboxes[i][3] + split_x[k]}\n")
    pred_file.close() 
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, November 21st 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import torch
from torch.autograd import Variable
import queue
import cv2
import numpy as np
import time
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import NullLocator

from libs.YOLOv3.models import Darknet
from libs.YOLOv3.utils.utils import load_classes, non_max_suppression, rescale_boxes
from core.edge_component import EdgeComponent

class YOLOv3(EdgeComponent):
    def __init__(self, app):
        super().__init__(app, 'YOLOv3')
    
    def _initialize(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Darknet(self.config['model_def'], img_size=self.config['img_size']).to(device)
        self.model.load_darknet_weights(self.config['weights_path'])
        self.model.eval() # set eval mode
        self.classes = load_classes(self.config['class_path'])
        self.detect_cache = queue.Queue()

    def _detect(self, frame):
        Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor
        input_img = Variable(frame.type(Tensor))
        with torch.no_grad():
            start_time = time.time()
            detections = self.model(input_img)
            detections = non_max_suppression(detections, self.config['conf_thres'], self.config['nms_thres'])
            # detections = np.array([d.numpy() for d in detections])
            end_time = time.time()
            self.logger.info("detection takes {} seconds".format(end_time - start_time))

        return detections
    
    def draw_detection(self, img, detections):
        # ax.imshow(img)
        cmap = plt.get_cmap("tab20b")
        colors = [cmap(i) for i in np.linspace(0, 1, 20)]
        if detections is not None:
            # Rescale boxes to original image
            detections = rescale_boxes(detections, self.config['img_size'], img.shape[:2])
            unique_labels = detections[:, -1].cpu().unique()
            n_cls_preds = len(unique_labels)
            bbox_colors = random.sample(colors, n_cls_preds)
            for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:

                print("\t+ Label: %s, Conf: %.5f" % (self.classes[int(cls_pred)], cls_conf.item()))

                box_w = x2 - x1
                box_h = y2 - y1

                color = bbox_colors[int(np.where(unique_labels == int(cls_pred))[0])]
                # Create a Rectangle patch
                img = cv2.rectangle(img, (x1, y1), (x1 + box_w, y1 + box_h), (0, 255, 0), 2)
                # Add the bbox to the plot
            cv2.imwrite('output.jpg', img)

  
    
    def detect(self, raw_frame):
        frame = cv2.resize(raw_frame, (self.config['img_size'], self.config['img_size']))
        detections = self.detect(torch.from_numpy(np.expand_dims(np.transpose(frame, [2, 1, 0]), 0)))[0]
        self.draw_detection(raw_frame, detections)
        self.logger.info("do detect.")
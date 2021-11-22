#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, July 20th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''
from pathlib import Path
import coremltools
import cv2

model_path = '/Users/wangxu/Edge/EdgeTileIOS/mlmodel/YOLOv3/YOLOv3.mlmodel'

model_path = Path(model_path)

print(model_path.exists())

model = coremltools.models.MLModel(str(model_path))

# Make prediction
img = cv2.imread('/Users/wangxu/Edge/EdgeTileClient/data/jpg/img232.jpg')
_, predictions, _ = model.predict({'image':img})

print(predictions)
# model.visualize_spec()

#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, April 9th 2020
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2020 Institute of Trustworthy Network and System, Tsinghua University
'''

import numpy as np
from fvcore.common.file_io import PathManager
import xml.etree.ElementTree as ET


def parse_rec(filename):
    """Parse a PASCAL VOC xml file."""
    with PathManager.open(filename) as f:
        tree = ET.parse(f)
    objects = []
    for obj in tree.findall("object"):
        obj_struct = {}
        obj_struct["name"] = obj.find("name").text
        obj_struct["difficult"] = 0 # int(float(obj.find("occlusion").text) < 0.5)
        bbox = obj.find("bndbox")

        obj_struct["bbox"] = [
            int(float(bbox.find("xmin").text)),
            int(float(bbox.find("ymin").text)),
            int(float(bbox.find("xmax").text)),
            int(float(bbox.find("ymax").text)),
        ]
        
        objects.append(obj_struct)

    return objects


def voc_ap(rec, prec, use_07_metric=False):
    """Compute VOC AP given precision and recall. If use_07_metric is true, uses
    the VOC 07 11-point method (default:False).
    """
    if use_07_metric:
        # 11 point metric
        ap = 0.0
        for t in np.arange(0.0, 1.1, 0.1):
            if np.sum(rec >= t) == 0:
                p = 0
            else:
                p = np.max(prec[rec >= t])
            ap = ap + p / 11.0
    else:
        # correct AP calculation
        # first append sentinel values at the end
        mrec = np.concatenate(([0.0], rec, [1.0]))
        mpre = np.concatenate(([0.0], prec, [0.0]))

        # compute the precision envelope
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

        # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        i = np.where(mrec[1:] != mrec[:-1])[0]

        # and sum (\Delta recall) * prec
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap


def voc_eval(detpath, annopath, imagesetfile, classname, ovthresh=0.5, use_07_metric=False):
    """rec, prec, ap = voc_eval(detpath,
                                annopath,
                                imagesetfile,
                                classname,
                                [ovthresh],
                                [use_07_metric])
    Top level function that does the PASCAL VOC evaluation.
    detpath: Path to detections
        detpath.format(classname) should produce the detection results file.
    annopath: Path to annotations
        annopath.format(imagename) should be the xml annotations file.
    imagesetfile: Text file containing the list of images, one image per line.
    classname: Category name (duh)
    [ovthresh]: Overlap threshold (default = 0.5)
    [use_07_metric]: Whether to use VOC07's 11 point AP computation
        (default False)
    """
    # assumes detections are in detpath.format(classname)
    # assumes annotations are in annopath.format(imagename)
    # assumes imagesetfile is a text file with each line an image name

    # first load gt
    # read list of images
    with PathManager.open(imagesetfile, "r") as f:
        lines = f.readlines()
    imagenames = [x.strip() for x in lines]

    # load annots
    recs = {}
    for imagename in imagenames:
        recs[imagename] = parse_rec(annopath.format(imagename))

    # extract gt objects for this class
    class_recs = {}
    npos = 0
    for imagename in imagenames:
        R = [obj for obj in recs[imagename] if obj["name"] == classname]
        bbox = np.array([x["bbox"] for x in R])
        difficult = np.array([x["difficult"] for x in R]).astype(np.bool)
        # difficult = np.array([False for x in R]).astype(np.bool)  # treat all "difficult" as GT
        det = [False] * len(R)
        npos = npos + sum(~difficult)
        class_recs[imagename] = {"bbox": bbox, "difficult": difficult, "det": det}

    # read dets
    detfile = detpath.format(classname)
    with open(detfile, "r") as f:
        lines = f.readlines()

    splitlines = [x.strip().split(" ") for x in lines]
    image_ids = np.array([x[0] for x in splitlines])
    confidence = np.array([float(x[1]) for x in splitlines])
    BB = np.array([[float(z) for z in x[2:]] for x in splitlines]).reshape(-1, 4)

    # image_ids = image_ids[confidence>0.55]
    # BB = BB[confidence>0.55]
    # confidence = confidence[confidence>0.55]
    # sort by confidence
    sorted_ind = np.argsort(-confidence)
    BB = BB[sorted_ind, :]
    image_ids = [image_ids[x] for x in sorted_ind]

    # go down dets and mark TPs and FPs
    nd = len(image_ids)
    tp = np.zeros(nd)
    fp = np.zeros(nd)
    for d in range(nd):
        R = class_recs[f"{int(image_ids[d]):06d}"]
        bb = BB[d, :].astype(float)
        ovmax = -np.inf
        BBGT = R["bbox"].astype(float)

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
            ovmax = np.max(overlaps)
            jmax = np.argmax(overlaps)

        if ovmax > ovthresh:
            if not R["difficult"][jmax]:
                if not R["det"][jmax]:
                    tp[d] = 1.0
                    R["det"][jmax] = 1
                else:
                    fp[d] = 1.0
        else:
            fp[d] = 1.0

    # compute precision recall
    fp = np.cumsum(fp)
    tp = np.cumsum(tp)
    rec = tp / float(npos)
    # print(npos)
    # avoid divide by zero in case the first detection matches a difficult
    # ground truth
    prec = tp / np.maximum(tp + fp, np.finfo(np.float64).eps)
    ap = voc_ap(rec, prec, use_07_metric)

    return rec, prec, ap

def evaluate_exp(exp_name):
    class_file = '/Users/wangxu/Edge/EdgeTileClient/data/drone/track/' + exp_name + '/{0}.txt'
    gt_file = '/Users/wangxu/Edge/EdgeTileClient/data/drone/anno720p/uav0000137_00458_v/{0}.xml'
    img_set_file = '/Users/wangxu/Edge/EdgeTileClient/data/drone/track/' + exp_name + '/img_set.txt'
    class_name = 'car'
    rec, prec, ap_car = voc_eval(class_file, gt_file, img_set_file, class_name);
    #print(len(rec)) 
    class_name = 'pedestrian'
    rec, prec, ap_person = voc_eval(class_file, gt_file, img_set_file, class_name);
    print(f"{exp_name}: car {ap_car} pedestrian {ap_person}")
    # print(len(rec))
    

if __name__ == '__main__':
    # exp_name = 'no_group_exp1'
    # evaluate_exp(exp_name)
    # exp_name = 'no_group_exp2'
    # evaluate_exp(exp_name)
    # exp_name = 'no_group_exp3'
    # evaluate_exp(exp_name)

    # # exp_name = '4group_no_parallel'
    # # evaluate_exp(exp_name)
    # exp_name = '4group_parallel1'
    # evaluate_exp(exp_name)
    # exp_name = '4group_parallel2'
    # evaluate_exp(exp_name)
    # exp_name = '4group_parallel3'
    # evaluate_exp(exp_name)
    # exp_name = '4group_parallel_revert1'
    # evaluate_exp(exp_name)
    # exp_name = '4group_parallel_revert2'
    # evaluate_exp(exp_name)
    # exp_name = '4group_parallel_revert3'
    # evaluate_exp(exp_name)
    # exp_name = '4group_dynamic1'
    # evaluate_exp(exp_name)
    # exp_name = '4group_dynamic2'
    # evaluate_exp(exp_name)
    # exp_name = 'yolo_detector'
    # evaluate_exp(exp_name)
    # exp_name = 'yolo_server'
    # evaluate_exp(exp_name)
    # exp_name = '1static_server_1'
    # evaluate_exp(exp_name)
    # exp_name = ['server_1s_1', 'server_1s_2', 'server_1s_3', 'server_4s_1', 'server_4s_2', 'server_4s_3', 'server_4d_1', 'server_4d_2', 'server_4d_3', 'local_1', 'local_2', 'local_3', 'both_1s_1', 'both_1s_2', 'both_1s_3', 'both_4s_1', 'both_4s_2', 'both_4s_3', 'both_4d_1', 'both_4d_2', 'both_4d_3', '4d_frcnn_1', '4d_frcnn_2', '4d_frcnn_3']
    # for exp in exp_name:
    #     evaluate_exp(exp)
    
    
    # exp_name = ['default']
    # for exp in exp_name:
    #     evaluate_exp(exp)
    
    # exp_name = ['server_1s_4', 'server_1s_5', 'server_4s_4', 'server_4s_5', 'server_4d_4', 'server_4d_5', 'both_4d_7']
    # for exp in exp_name:
    #     evaluate_exp(exp)
    
    exp_name = ['server_1s_1', 'server_1s_2', 'server_4s_1', 'server_4s_2', 'server_4d_1', 'server_4d_2', 'local_1', 'local_2', 'both_1s_1', 'both_1s_2', 'both_4s_1', 'both_4s_2', 'both_4d_1', 'both_4d_2']
    for exp in exp_name:
        evaluate_exp(exp)

    # with open("data/mot17/img_set.txt", 'w') as f:
    #     for i in range(600):
    #         f.write(f'{i:06d}\n')
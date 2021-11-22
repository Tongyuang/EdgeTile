'''
This file is used to implement optical flow track in Glimpse.
'''
from fvcore.common.file_io import PathManager
import xml.etree.ElementTree as ET
import numpy as np
import json
import time
import cv2
import math
from xml.dom import minidom

import os

class BBox:
    def __init__(self, box_dict=None):
        super().__init__()
        self.class_name = None
        self.xmin = 0
        self.xmax = 0
        self.ymin = 0
        self.ymax = 0
        self.confidence = 0 
        self.key_points = []
        if box_dict is not None:
            self.class_name = box_dict["class_name"]
            self.xmin = box_dict["xmin"]
            self.xmax = box_dict["xmax"]
            self.ymin = box_dict["ymin"]
            self.ymax = box_dict["ymax"]
            self.confidence = box_dict["confidence"] 
            self.key_points = box_dict["key_points"]

def load_gt_box(filename, load_key_points=False, frame=None):
    """Parse a PASCAL VOC xml file."""
    with PathManager.open(filename) as f:
        tree = ET.parse(f)
    objects = []
    for obj in tree.findall("object"):
        bbox = obj.find("bndbox")
        obj_struct = {}
        obj_struct["class_name"] = obj.find("name").text
        obj_struct["confidence"] = 0 
        obj_struct["xmin"] = float(bbox.find("xmin").text)
        obj_struct["ymin"] = float(bbox.find("ymin").text)
        obj_struct["xmax"] = float(bbox.find("xmax").text)
        obj_struct["ymax"] = float(bbox.find("ymax").text)
        if load_key_points:
            # get key points
            xmin = obj_struct["xmin"]
            ymin = obj_struct["ymin"]
            xmax = obj_struct["xmax"]
            ymax = obj_struct["ymax"]
            im_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 26 feature points + 4 corners of bounding box
            features_to_track = 26
            im_roi = im_gray[
                int(ymin):int(ymax),
                int(xmin):int(xmax),
            ]  # image is stored as (y, x)
            key_points = cv2.goodFeaturesToTrack(
                im_roi, features_to_track, 0.01, 10)
            bbox_corners = np.array(
                [[(xmin, ymin)], [(xmin, ymax)], [(xmax, ymin)],
                [(xmax, ymax)]],
                dtype=np.float32)

            # sometimes the im_roi has no corners so  key_points is None
            if key_points is None:
                key_points = bbox_corners
            else:
                # update to the key point coordinate in original image
                for kp in key_points:
                    kp += np.array([xmin, ymin])
            key_points = np.vstack((key_points, bbox_corners))
            key_points_list = []
            for point in key_points:
                # 注意到point是以列表为元素的列表，所以需要flatten或者ravel一下。
                x, y = point.flatten()
                key_points_list.append((float(x),float(y)))
            obj_struct["key_points"] = key_points_list
        objects.append(obj_struct)
    
    return objects



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

def evaluate(gt_boxes, client_boxes, iou_thres):
    total_tp_car = 0
    total_pred_car = 0
    total_gt_car = 0
    total_tp_person = 0
    total_pred_person = 0
    total_gt_person = 0
    
    iou_list = []
    for frame_id in gt_boxes.keys():
        # print(frame_id)
        tp_car, gt_car, pred_car, tp_person, gt_person, pred_person, iou_array = calculate_iou(client_boxes[frame_id], gt_boxes[frame_id], iou_thres=0.5) 
        # print(f"frame {frame_id}",[tp_car, gt_car, pred_car, tp_person, gt_person, pred_person, iou_array])
        iou_list += iou_array
        total_tp_car += tp_car
        total_tp_person += tp_person
        total_gt_car += gt_car
        total_gt_person += gt_person
        total_pred_car += pred_car
        total_pred_person += pred_person
    print("total_pred_car ", total_pred_car)  
    precision_car = total_tp_car / total_pred_car
    recall_car = total_tp_car / total_gt_car
    f1_car = 2 * precision_car * recall_car / (precision_car + recall_car)

    precision_person = total_tp_person / total_pred_person
    recall_person = total_tp_person / total_gt_person
    f1_person = 2 * precision_person * recall_person / (precision_person + recall_person)

    precision = (total_tp_person+total_tp_car)/(total_pred_car+total_pred_person)
    recall = (total_tp_car+total_tp_person)/(total_gt_car+total_gt_person)
    f1 = 2 * precision * recall / (precision + recall)

    print("cat\tprec\trec\tF1")
    print("car\t{:.4f}\t{:.4f}\t{:.4f}".format(precision_car, recall_car, f1_car))
    print("person\t{:.4f}\t{:.4f}\t{:.4f}".format(precision_person, recall_person, f1_person))
    print("total\t{:.4f}\t{:.4f}\t{:.4f}".format(precision, recall, f1))
    print("iou_accu:{:.4f}".format(sum(iou_list)/len(iou_list)))

def calculateSD(numArray):
    num_sum = 0.0
    standardDeviation = 0.0
    length = len(numArray)
    for num in numArray:
        num_sum+=num
    mean = num_sum / length
    for num in numArray:
        standardDeviation += pow(num-mean, 2)
    return math.sqrt(standardDeviation/length)

def track_update(init_boxes_dict, preFrame, newFrame):
    init_boxes = []
    for b in init_boxes_dict:
        init_boxes.append(BBox(b))
    result_boxes = []
    suc = True
    prevKeyPtsConList = []
    curKeyPtsConList = []
    curRectList = []
    curClassLabels = []
    
    curConfidences = []
    curKeyPtsList = []

    for box in init_boxes:
        for key_point in box.key_points:
            prevKeyPtsConList.append([key_point])
    # print(f"preFrame has {len(prevKeyPtsConList)} keypoints")
    if len(prevKeyPtsConList) == 0:
        print("No key points!")
        return []
    
    
    # Perform LK-tracking
    lk_params = {"winSize": (31, 31),
                 "maxLevel": 3,
                 "criteria": (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03),
                 "flags":0, 
                 "minEigThreshold":0.001}
    prevPts = np.float32([tr[-1] for tr in prevKeyPtsConList]).reshape(-1, 1, 2)       
    curKeyPtsConList, statusList, err = cv2.calcOpticalFlowPyrLK(preFrame,
                                            newFrame,
                                            prevPts,
                                            None,
                                            **lk_params)
    
    offset = 0
    for box in init_boxes:
        lenObjKeyPts = len(box.key_points)
        movements = []
        curObjSucPtsList = []
        left = 10000.0
        right = 0
        top = 10000.0
        bottom = 0
        for j in range(offset, offset+lenObjKeyPts):
            if statusList[j][0]:
                prevP = prevKeyPtsConList[j][0]
                curP = curKeyPtsConList[j][0]
                
                
                distance = math.sqrt((prevP[0] - curP[0]) * (prevP[0] - curP[0]) +
                                       (prevP[1] - curP[1]) * (prevP[1] - curP[1]))
                movements.append(distance)
                curObjSucPtsList.append(curP)
                if curP[0] < left:
                    left = curP[0]
                if curP[0] > right:
                    right = curP[0]
                if curP[1] < top:
                    top = curP[1]
                if curP[1] > bottom:
                    bottom = curP[1]

        # stdMov = calculateSD(movements)
        
        rectWidth = 0
        rectHeight = 0
        rectWidth = int(right - left)
        rectHeight = int(bottom - top)
        
        if len(curObjSucPtsList) >= 4 and min(rectWidth, rectHeight) > 5:
            curRectList.append([left, top, right, bottom])
            curClassLabels.append(box.class_name)
            curConfidences.append(box.confidence)
            curKeyPtsList.append(curObjSucPtsList)
        else:
            curRectList.append([box.xmin, box.ymin, box.xmax, box.ymax])
            curClassLabels.append(box.class_name)
            curConfidences.append(box.confidence)
            curKeyPtsList.append(curObjSucPtsList)
        
        
        offset += lenObjKeyPts
    
    for i in range(0, len(curRectList)):
        curRect = curRectList[i]
        box = {}
        box["xmin"] = float(curRect[0])
        box["ymin"] = float(curRect[1])
        box["xmax"]  = float(curRect[2])
        box["ymax"] = float(curRect[3])
        box["confidence"] = curConfidences[i]
        box["class_name"] = curClassLabels[i]
        box["key_points"] = []
        for j in range(0, len(curKeyPtsList[i])):
            box["key_points"].append(tuple(curKeyPtsList[i][j]))
        
        result_boxes.append(box) 
    return result_boxes

def export_xml(all_client_boxes, box_dir):
    import shutil
    if os.path.exists(box_dir):
        shutil.rmtree(box_dir)  
    os.mkdir(box_dir)
    for frame_id in all_client_boxes.keys():
        dst_file = '{}/{:06d}.xml'.format(box_dir,frame_id)
        anno = ET.Element('annotation')
        for obj in all_client_boxes[frame_id]:
            obj_ele = ET.SubElement(anno, 'object')
            track_id = ET.SubElement(obj_ele, 'trackid')
            track_id.text = str(-1)
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

if __name__ == "__main__":
    edge_latency = 313.9009
    exp_name = 'Glimpse-wifi802-40000'
    fps = 60
    frames_num = 848
    tracker_latency = 80

    track_step = int(tracker_latency/(1000/fps)) * int(120/fps)
    server_step = int(edge_latency/(1000/fps)) * int(120/fps)
    
    # server_step = 1
    # track_step = 0
    print(f"server_step = {server_step}")
    print(f"track_step = {track_step}")
    video_path = "/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/video_2k_120fps/uav0000138_00000_v.mp4"
    anno_path = "/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/yolov3_spp_anno_2k_120fps/uav0000138_00000_v"
    
    all_gt_boxes = {}
    all_client_boxes = {}
    
    cap = cv2.VideoCapture(str(video_path))  # 打开指定路径上的视频文件
    frame_id = 0
    frame_cache = []
    init_boxes = []
    update_boxes = []

    full_step_flag = False
    
    while True:
        ret, frame = cap.read()
        if ret == True:
            frame_cache.append(frame)
        else:
            break
    print("frame cache loaded!")
    while frame_id < len(frame_cache):
        frame = frame_cache[frame_id]
        if frame_id >= server_step and frame_id % int(120/fps) == 0:
            # print(f"track frame {frame_id}")
            # gt_boxes = load_gt_box(filename=anno_path+'/{:06d}.xml'.format(frame_id))
            # all_gt_boxes[frame_id] = gt_boxes
            if frame_id % server_step == 0 or full_step_flag:
                full_step_flag = False
                refer_id = int(frame_id / server_step - 1 ) * server_step
                print(f"track frame {frame_id} from {refer_id}")
                preFrame = frame_cache[refer_id]
                midFrame = frame_cache[int((frame_id+refer_id)/2)]
                newFrame = frame
                init_boxes = load_gt_box(filename=anno_path+'/{:06d}.xml'.format(refer_id), \
                    load_key_points=True, frame=preFrame) 
                # init_boxes = track_update(init_boxes, preFrame, midFrame)
                # update_boxes = track_update(init_boxes, midFrame, frame)
                update_boxes = track_update(init_boxes, preFrame, frame)
            else:
                print(f"track frame {frame_id} from {last_frame_id}")
                preFrame = frame_cache[last_frame_id]
                newFrame = frame
                update_boxes = track_update(init_boxes, preFrame, newFrame)
                for x in range(frame_id, frame_id+track_step+1):
                    if x % server_step == 0:
                        full_step_flag = True
                        print(f"frame {x} is passed..")
            pre_boxes = init_boxes
            init_boxes = update_boxes
            
            for x in range(frame_id, min(frame_id+track_step+1, frames_num)):
                if x % int(120/fps) == 0:
                    gt_boxes = load_gt_box(filename=anno_path+'/{:06d}.xml'.format(x))
                    all_gt_boxes[x] = gt_boxes
                    all_client_boxes[x] = pre_boxes
            if frame_id + track_step < frames_num:
                all_client_boxes[frame_id + track_step] = update_boxes
            
                
            print(f"give frame {frame_id} boxes to frame {frame_id + track_step}")
            last_frame_id = frame_id + track_step
            # print(update_boxes)
            frame_id += (track_step + 1)
            # f = frame_cache[frame_id + track_step]
            # for box in update_boxes:
            #     p1 = tuple([int(box["xmin"]), int(box["ymin"])])
            #     p2 = tuple([int(box["xmax"]), int(box["ymax"])])
            #     cv2.rectangle(f, p1, p2, (255, 0, 0), 2)
            # cv2.imshow("video", f)
            # if cv2.waitKey(100) & 0xFF == ord('q'):
            #     break
        else:
            frame_id += 1


    

    print("last evaluate:")
    evaluate(all_gt_boxes, all_client_boxes, 0.5)
    export_xml(all_client_boxes, '{}'.format(exp_name))

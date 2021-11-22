'''
This file is used to implement motion vector track in EAAR.

Average object latency is set to 220.96ms. (Test: 220.963033ms), so in 120fps video, it will pass about 220.96/(1000/120)≈27 frames.
'''
from fvcore.common.file_io import PathManager
import xml.etree.ElementTree as ET
import numpy as np
import json
import time
import os
from xml.dom import minidom
def load_gt_box(filename):
    """Parse a PASCAL VOC xml file."""
    with PathManager.open(filename) as f:
        tree = ET.parse(f)
    objects = []
    for obj in tree.findall("object"):
        bbox = obj.find("bndbox")
        obj_struct = {}
        obj_struct["class_name"] = obj.find("name").text
        obj_struct["difficult"] = 0 
        obj_struct["xmin"] = float(bbox.find("xmin").text)
        obj_struct["ymin"] = float(bbox.find("ymin").text)
        obj_struct["xmax"] = float(bbox.find("xmax").text)
        obj_struct["ymax"] = float(bbox.find("ymax").text)
        objects.append(obj_struct)
    return objects

def load_mv(filepath):
    # 直接从json文件中读取数据返回一个python对象
    mv_data = json.load(open(filepath))
    return mv_data

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
        tp_car, gt_car, pred_car, tp_person, gt_person, pred_person, iou_array = calculate_iou(client_boxes[frame_id], gt_boxes[frame_id], iou_thres=0.5) 
        iou_list += iou_array
        total_tp_car += tp_car
        total_tp_person += tp_person
        total_gt_car += gt_car
        total_gt_person += gt_person
        total_pred_car += pred_car
        total_pred_person += pred_person
        
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

def track_update(init_boxes, frame_id, refer_id, mv_path):
    print("track from frame {} to frame {}...".format(refer_id, frame_id))
    update_boxes = []
    filepath = mv_path + "/{}-{}/2.json".format(refer_id, frame_id)
    # motion_vectors = all_motion_vectors[frame_id]
    motion_vectors = load_mv(filepath)
    
    for box in init_boxes:
        xmin = box["xmin"]
        ymin = box["ymin"]
        xmax = box["xmax"]
        ymax = box["ymax"]
        dxs = []
        dys = []
        for vec in motion_vectors:
            src_x = int(vec["src_x"])
            src_y = int(vec["src_y"])
            dst_x = int(vec["dst_x"])
            dst_y = int(vec["dst_y"])
            if src_x >= xmin and src_x <= xmax and \
                src_y >= ymin and src_y <= ymax and \
                dst_x >= xmin and dst_x <= xmax and \
                dst_y >= ymin and dst_y <= ymax:
                dxs.append(dst_x - src_x)
                dys.append(dst_y - src_y)
        if len(dxs) != 0:
            mean_dx = np.mean(dxs)
            mean_dy = np.mean(dys)
        else:
            mean_dx = 0
            mean_dy = 0
        
        update_box = {}
        update_box["class_name"] = box["class_name"]
        update_box["difficult"] = box["difficult"]
        
        update_box["xmin"] = xmin + mean_dx
        update_box["ymin"] = ymin + mean_dy
        update_box["xmax"] = xmax + mean_dx
        update_box["ymax"] = ymax + mean_dy
        update_boxes.append(update_box)
    return update_boxes
def export_xml(all_client_boxes, box_dir):
    import shutil
    if os.path.exists(box_dir):
        shutil.rmtree(box_dir)  
    os.mkdir(box_dir)
    for frame_id in all_client_boxes.keys():
        dst_file = '{}/{:06d}.xml'.format(box_dir, frame_id)
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
    edge_latency = 809.2515
    fps = 60
    exp_name = 'EAAR-wifi802-8000'
    server_step = int(edge_latency/(1000/fps)) * int(120/fps)
    print(f"server_step: {server_step}")
    mv_path = "source_frames_{}".format(exp_name)
    anno_path = "/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/yolov3_spp_anno_2k_120fps/uav0000138_00000_v"
    frames_num = 848
    all_gt_boxes = {}
    all_client_boxes = {}
    # motion_vectors = {}
    # for frame_id in range(0, frames_num):
    #     t1 = time.time()*1000
    #     mv_data = load_mv(mv_path+'/{}.json'.format(frame_id+1))
    #     t2 = time.time()*1000
    #     print("load mv of frame {}...[{:.4f} ms]".format(frame_id,t2-t1))
    #     motion_vectors[frame_id] = mv_data
    # print("load mvs done!")
    init_boxes = []
    refer_id = 0
    for frame_id in range(0, frames_num):
        if frame_id >= server_step and frame_id % int(120/fps) == 0:
            gt_boxes = load_gt_box(anno_path+'/{:06d}.xml'.format(frame_id))
            all_gt_boxes[frame_id] = gt_boxes
            if frame_id%server_step == 0:
                refer_id = int(frame_id / server_step-1)*server_step
                init_boxes = load_gt_box(anno_path+'/{:06d}.xml'.format(refer_id))
                # client_boxes = track_update(init_boxes, i)
                # client_boxes = init_boxes
                # for i in range(frame_id-server_step+1, frame_id):
                    # print("track {}".format(i))
                    # init_boxes = track_update(init_boxes, i, motion_vectors)
            
                # print("real track {}".format(frame_id))
            client_boxes = track_update(init_boxes, frame_id, refer_id, mv_path)
                # init_boxes = client_boxes
            all_client_boxes[frame_id] = client_boxes
            # if frame_id%20 == 0:
            #     evaluate(all_gt_boxes, all_client_boxes, 0.5)

    print("last evaluate:")
    evaluate(all_gt_boxes, all_client_boxes, 0.5)
    export_xml(all_client_boxes,'{}'.format(exp_name))

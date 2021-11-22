# this is used to get precision of the render result.
import numpy as np
import xml.etree.ElementTree as ET
import pathlib
import os


def load_ground_truth(anno_path):
    ground_truth_dict = {}
    for root, dirs, files in os.walk(anno_path):
        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list
        print("hello world")
        # 遍历文件
        for f in files:
            frame = int(f.split('.xml')[0])
            xml_path = os.path.join(root, f)
            tree = ET.parse(xml_path)
            track_item = {}
            for item in tree.findall(".//object"):
                track_id = int(item.find("./trackid").text)
                xmax = float(item.find(".//xmax").text)
                xmin = float(item.find(".//xmin").text)
                ymax = float(item.find(".//ymax").text)
                ymin = float(item.find(".//ymin").text)
                box_item = {}
                box_item['xmax'] = xmax
                box_item['xmin'] = xmin
                box_item['ymax'] = ymax
                box_item['ymin'] = ymin

                track_item[track_id] = box_item
            
            ground_truth_dict[frame] = track_item
            
    
    return ground_truth_dict


def load_client_boxes(client_box_path):
    client_box_dict = {}
    with open(client_box_path, 'r', encoding='utf-8') as f:
        for line in f:
            frame = int(line.split(',')[0])
            if frame not in client_box_dict.keys():
                client_box_dict[frame] = {}
            trackid = int(line.split(',')[1])
            xmin = float(line.split(',')[2])
            xmax = float(line.split(',')[3])
            ymin = float(line.split(',')[4])
            ymax = float(line.split(',')[5])
            box_item = {}
            box_item['xmax'] = xmax
            box_item['xmin'] = xmin
            box_item['ymax'] = ymax
            box_item['ymin'] = ymin
            
            client_box_dict[frame][trackid] = box_item
            
    return client_box_dict


def compute_iou(gt_box, b_box):
    '''
    计算iou
    :param gt_box: ground truth gt_box = [x0,y0,x1,y1]（x0,y0)为左上角的坐标（x1,y1）为右下角的坐标
    :param b_box: bounding box b_box 表示形式同上
    :return: 
    '''
    width0 = gt_box[2]-gt_box[0]
    height0 = gt_box[3] - gt_box[1]
    width1 = b_box[2] - b_box[0]
    height1 = b_box[3] - b_box[1]
    max_x = max(gt_box[2], b_box[2])
    min_x = min(gt_box[0], b_box[0])
    width = width0 + width1 - (max_x-min_x)
    max_y = max(gt_box[3], b_box[3])
    min_y = min(gt_box[1], b_box[1])
    height = height0 + height1 - (max_y - min_y)

    interArea = width * height
    boxAArea = width0 * height0
    boxBArea = width1 * height1
    iou = interArea / (boxAArea + boxBArea - interArea)
    return iou



def cal_detect_precision(ground_truth_dict, client_box_path):
    print(client_box_path)
    # load client box.
    client_box_dict = load_client_boxes(client_box_path)
    total_box = 0
    right_box = 0
    useful_box = 0
    for frame in client_box_dict.keys():
        for trackid in client_box_dict[frame].keys():
            total_box += 1

            client_box_xmin = client_box_dict[frame][trackid]['xmin']
            client_box_xmax = client_box_dict[frame][trackid]['xmax']
            client_box_ymin = client_box_dict[frame][trackid]['ymin']
            client_box_ymax = client_box_dict[frame][trackid]['ymax']
            assert(client_box_xmin <= client_box_xmax)
            assert(client_box_ymin <= client_box_ymax)
            
            b_box = [client_box_xmin, client_box_ymin,
                     client_box_xmax, client_box_ymax]
            
            if trackid not in ground_truth_dict[frame].keys():  # 参考帧的目标已经消失
                continue
            gt_xmin = ground_truth_dict[frame][trackid]['xmin']
            gt_xmax = ground_truth_dict[frame][trackid]['xmax']
            gt_ymin = ground_truth_dict[frame][trackid]['ymin']
            gt_ymax = ground_truth_dict[frame][trackid]['ymax']
            gt_box = [gt_xmin, gt_ymin, gt_xmax, gt_ymax]
            
            assert(gt_xmin <= gt_xmax)
            assert(gt_ymin <= gt_ymax)

            iou = compute_iou(gt_box, b_box)
            useful_box += 1
            if iou > 0.5:
                right_box += 1
    print("total client boxes:{}".format(total_box))
    print("useful client boxes:{}".format(useful_box))
    print("right client boxes:{}".format(right_box))
    print("Precision: {:.4f}".format(float(right_box/total_box)))
    print("===========================================")

    return float(right_box/total_box)


if __name__ == "__main__":
    # load ground truth.
    anno_path = "../EdgeTileClient/data/drone/anno/"
    video_name = "uav0000137_00458_v"
    frame_anno_path = pathlib.Path(anno_path) / pathlib.Path(video_name)
    ground_truth_dict = load_ground_truth(frame_anno_path)
    


    print("=== ONLY CLIENT ===")

    detect_precision = cal_detect_precision(
        ground_truth_dict=ground_truth_dict,
        client_box_path="AnalyzeUtils/tracker_logs/client_boxes_1.log"
    )

    detect_precision = cal_detect_precision(
        ground_truth_dict=ground_truth_dict,
        client_box_path="AnalyzeUtils/tracker_logs/client_boxes.log"
    )

    detect_precision = cal_detect_precision(
        ground_truth_dict=ground_truth_dict,
        client_box_path="AnalyzeUtils/tracker_logs/client_boxes_5.log"
    )

    detect_precision = cal_detect_precision(
        ground_truth_dict=ground_truth_dict,
        client_box_path="AnalyzeUtils/tracker_logs/client_boxes_10.log"
    )

    
    
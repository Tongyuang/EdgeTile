
import cv2
import os
import sys
import shutil
from os.path import join, getsize
import xml.etree.ElementTree as ET
from pathlib import Path
def get_imgs(video_path):
    shutil.rmtree('img')  
    os.mkdir('img')
    
    cap = cv2.VideoCapture(str(video_path))  # 打开指定路径上的视频文件
    frame_id = 0
    while True:
        ret, frame = cap.read()
        if ret == True:
            cv2.imwrite("img/{:06d}.jpg".format(frame_id), frame)
            frame_id += 1
        else:
            break

def get_meta():
    direc = 'img_ffmpeg'
    frame_id = 0
    server_step = 24
    size = 0
    file_size_dict = {}
    files_num = 0
    for root, dirs, files in os.walk(direc):
        files_num = len(files)
        for name in files:
            file_size = getsize(join(root, name))
            frame_id = int(name.split('.jpg')[0])
            file_size_dict[frame_id-1] = file_size
    print(file_size_dict)
    with open('output/uav0000138_00000_v.meta','w',encoding='utf-8') as f:
        f.write('0,-1,263\n')
        for i in range(0, files_num, server_step):
            f.write('{},{},{}\n'.format(i, 0, file_size_dict[i]))
        
        
def analyze_latency(read_timestamps_file, recv_timestamps_file):
    read_timestamps = {}

    with open(read_timestamps_file, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline().split('\n')[0]
            if line == '':
                break
            frame_id = int(line.split(' ')[0])
            timestamp = int(line.split(' ')[1])
            read_timestamps[frame_id] = timestamp
    total_box_num = 0
    total_latency = 0
    with open(recv_timestamps_file, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline().split('\n')[0]
            if line == '':
                break
            frame_id = int(line.split(' ')[0])
            group_id = int(line.split(' ')[1])
            timestamp = int(line.split(' ')[2])
            boxes_size = int(line.split(' ')[3])
            latency = timestamp - read_timestamps[frame_id]
            total_latency = total_latency + latency * boxes_size
            total_box_num = total_box_num + boxes_size
    average_object_latency = total_latency / total_box_num
    print("total latency: {}ms".format(total_latency))
    print("total object number: {}".format(total_box_num))
    print("average object latency: {:.4f}ms".format(average_object_latency))

def compute_meta():
    eaar_meta = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/output/meta_file/EAAR/uav0000138_00000_v.meta'
    edgeduet_meta = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/output/meta_file/EdgeDuet/uav0000138_00000_v.meta'
    eaar_size = 0
    edgeduet_size = 0
    with open(eaar_meta, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline().split('\n')[0]
            if line == '':
                break
            file_size = int(line.split(',')[2])
            eaar_size += file_size
    print('EAAR size: {} Bytes'.format(eaar_size))
    with open(edgeduet_meta, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline().split('\n')[0]
            if line == '':
                break
            file_size = int(line.split(',')[2])
            edgeduet_size += file_size
    print('EdgeDuet size: {} Bytes'.format(edgeduet_size))

def check_server_bbox(anno_path):
    for frame_id in range(0, 848):
        frame_anno_path = anno_path / "{:06d}.xml".format(frame_id)
        tree = ET.parse(frame_anno_path)
        for item in tree.findall(".//object"):
            class_name = item.find("./name").text
            track_id = int(item.find("./trackid").text)
            xmax = float(item.find(".//xmax").text)
            xmin = float(item.find(".//xmin").text)
            ymax = float(item.find(".//ymax").text)
            ymin = float(item.find(".//ymin").text)
            width = xmax - xmin
            height = ymax - ymin
            flag = (0 <= xmin and 0 <= width and xmax <= 2560 and \
                    0 <= ymin and 0 <= height and ymax <= 1440)
            if flag is False:
                print("roi error: [xmin={}, xmax={}, ymin={}, ymax={}]".format(xmin,\
                    xmax, ymin, ymax))
    print('check done!')

if __name__ == "__main__":
    video_path = '/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/video_2k_120fps/uav0000138_00000_v.mp4'
    anno_path = Path('/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/yolov3_spp_anno_2k_120fps/uav0000138_00000_v/')
    # check_server_bbox(anno_path)
    # get_imgs(video_path)
    # get_meta()
    
    # compute_meta()
    # input()
    
    print("EdgeDuet")
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EdgeDuet/read_timestamps1.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EdgeDuet/recv_timestamps1.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EdgeDuet/read_timestamps2.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EdgeDuet/recv_timestamps2.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EdgeDuet/read_timestamps3.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EdgeDuet/recv_timestamps3.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EdgeDuet/read_timestamps.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EdgeDuet/recv_timestamps.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)
    print("Glimpse")
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/GLIMPSE/read_timestamps1.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/GLIMPSE/recv_timestamps1.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/GLIMPSE/read_timestamps2.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/GLIMPSE/recv_timestamps2.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/GLIMPSE/read_timestamps3.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/GLIMPSE/recv_timestamps3.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)
    print("EAAR")
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EAAR/read_timestamps1.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EAAR/recv_timestamps1.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EAAR/read_timestamps2.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EAAR/recv_timestamps2.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)
    read_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EAAR/read_timestamps3.txt'
    recv_timestamps_file = '/Users/wujiahang/Project/EdgeTile/EdgeTileTools/VisDrone/data/EAAR/recv_timestamps3.txt'
    analyze_latency(read_timestamps_file, recv_timestamps_file)

    
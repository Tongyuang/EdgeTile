import cv2
import json



mv_dir = '/Users/wujiahang/Desktop/mv/{}.json'
video_dir = '/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/video_2k_120fps/uav0000138_00000_v.mp4'

cap = cv2.VideoCapture(str(video_dir))  # 打开指定路径上的视频文件
frame_id = 0
while True:
    ret, frame = cap.read()
    if ret == True:
        # 直接从json文件中读取数据返回一个python对象
        mv_data = json.load(open(mv_dir.format(frame_id + 1)))
        processed_frame = frame
        for vec in mv_data:
            source = vec['source']
            width = int(vec['width'])
            height = int(vec['height'])
            src_x = int(vec['src_x'])
            src_y = int(vec['src_y'])
            dst_x = int(vec['dst_x'])
            dst_y = int(vec['dst_y'])
            dx = int(vec['dx'])
            dy = int(vec['dy'])
            if dx!=0 or dy != 0:
                cv2.arrowedLine(processed_frame,(src_x,src_y), (dst_x,dst_y), (0,0,255),2,0,0,0.4)
        cv2.imwrite("frames/{:06d}.jpg".format(frame_id), processed_frame)
        frame_id += 1
    else:
        break
import cv2
import os
from pathlib import Path
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
        obj_struct["confidence"] = obj.find("confidence").text
        bbox = obj.find("bndbox")

        obj_struct["bbox"] = [
            int(float(bbox.find("xmin").text)),
            int(float(bbox.find("ymin").text)),
            int(float(bbox.find("xmax").text)),
            int(float(bbox.find("ymax").text)),
        ]
        
        objects.append(obj_struct)

    return objects

if __name__ == "__main__":
    video_path = '/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/video_2k_120fps/uav0000295_02300_v.mp4'
    client_box_path = '/Users/wujiahang/Project/EdgeTile/EdgeTileClient/data/drone/track/uav0000295_02300_v_tiles/client_boxes'
    
    # read video
    cap = cv2.VideoCapture(video_path)
    width =  int(cap.get(3))
    height = int(cap.get(4))
    fps = 120
    size = (int(width),int(height))
    videowriter = cv2.VideoWriter("a.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,size)
    frame_id = 0

    font_scale = 1
    font = cv2.FONT_HERSHEY_PLAIN


    while(True):
        # 读取帧
        ret, frame = cap.read()                        
        frame_file_name = Path(client_box_path)/'{:06d}.xml'.format(frame_id)
        
        if ret:
            if os.path.exists(frame_file_name):
                boxes = parse_rec(frame_file_name)
                for box in boxes:
                    cv2.rectangle(frame, (box["bbox"][0], box["bbox"][1]), (box["bbox"][2], box["bbox"][3]), (0, 0, 255), 2)
                    text = box["confidence"]
                    (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=3)[0]
                    cv2.putText(frame, text, (box["bbox"][0], box["bbox"][1] + text_height),  color=(0, 255, 255), fontFace=font, fontScale=font_scale)

            # frame2 = cv2.resize(frame, (int(width), int(height)))
            cv2.imshow('frame',frame)
            cv2.imwrite('img/{:06d}.jpg'.format(frame_id), frame)
            videowriter.write(frame)
            frame_id += 1
            # 按‘q’退出
            if cv2.waitKey(8) & 0xFF == ord('q'):          
                break
        else:
            break

    # 释放资源并关闭窗口
    cap.release()
    cv2.destroyAllWindows()

import sys
sys.path.insert(0, 'dist/python3')
import cv2
try:
    cap = cv2.VideoCapture('data/ILSVRC_sample/video/ILSVRC2015_val_00000000.mp4')
    print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
except Exception as e:
    print("exceptin")


import sys
sys.path.insert(0, 'dist/python3')
import cv2
try:
    cap = cv2.VideoCapture('data/test_video/test.mp4')
    print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
except Exception as e:
    print("exceptin")


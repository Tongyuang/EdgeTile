import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def loss(box, gt):
    ax, ay, aw, ah = box[0] + box[2] / 2, box[1] + box[3] / 2, box[2], box[3]
    tx, ty, tw, th = (gt[0][0] + gt[1][0]) / 2, (gt[0][1] + gt[1][1]) / 2, abs(gt[0][0] - gt[1][0]), abs(gt[0][1] - gt[1][1])
    d = []
    d.append((tx - ax) / aw)
    d.append((ty - ay) / ah)
    d.append(float(np.log(tw / aw)))
    d.append(float(np.log(th / ah)))
    for i in range(0, len(d)):
        if abs(d[i]) < 1:
            d[i] = 0.5 * d[i] ** 2
        elif abs(d[i]) >= 1:
            d[i] = abs(d[i]) - 0.5
    return sum(d)

def iou(Reframe, GTframe):
    """
    input format:[x, y, w, h]
    Change into [x1, y1, x2, y2]
    """

    # Change format
    Reframe[2], Reframe[3] = Reframe[0] + Reframe[2], Reframe[1] + Reframe[3]
    GTframe[2], GTframe[3] = GTframe[0] + GTframe[2], GTframe[1] + GTframe[3]

    x = sorted([Reframe[0], Reframe[2]])
    Reframe[0], Reframe[2] = x[0], x[1]
    y = sorted([Reframe[1], Reframe[3]])
    Reframe[1], Reframe[3] = y[0], y[1]

    x1, y1 = Reframe[0], Reframe[1]
    width1, height1 = Reframe[2] - Reframe[0], Reframe[3] - Reframe[1]
    
    x = sorted([GTframe[0], GTframe[2]])
    GTframe[0], GTframe[2] = x[0], x[1]
    y = sorted([GTframe[1], GTframe[3]])
    GTframe[1], GTframe[3] = y[0], y[1]

    x2, y2 = GTframe[0], GTframe[1]
    width2, height2 = GTframe[2] - GTframe[0], GTframe[3] - GTframe[1]

    endx = max(x1 + width1, x2 + width2)
    startx = min(x1, x2)
    width = width1 + width2 - (endx - startx)
    endy = max(y1 + height1, y2 + height2)
    starty = min(y1 , y2)
    height = height1 + height2 - (endy - starty)
    if width <=0 or height <= 0:
        ratio = 0
    else:
        Area = width * height
        Area1 = width1 * height1
        Area2 = width2 * height2
        ratio = Area * 1. / (Area1 + Area2 - Area)
    return ratio

class criteria_draw:
    def __init__(self, iou_list, threshold=0.5):
        self.iou_list = iou_list
        self.threshold = threshold

    def draw_EAO(self, class_name):
        if self.iou_list != None:
            frame_axis = np.linspace(1, len(self.iou_list), len(self.iou_list), endpoint=True)
            plt.xlim(1, len(self.iou_list))
            plt.ylim(0, 1)
            plt.plot(frame_axis, np.array(self.iou_list))
            plt.xlabel('frames')
            plt.ylabel('IOU')
            plt.savefig('E:\\code\\test_result_video\\' + class_name + '.png', dpi=120, bbox_inches='tight')
    
    def draw_from_file(self, name, mode):
        y1_list = []
        y2_list = []
        y3_list = []
        if mode == 'detect':
            with open('iou_with_detect.txt', 'r') as fp:
                while True:
                    str = fp.readline()
                    if len(str) == 0:
                        continue
                    if str[0] == '#':
                        break
                    y1_list.append(float(str))
            with open('iou_without_detect.txt', 'r') as fp:
                while True:
                    str = fp.readline()
                    if len(str) == 0:
                        continue
                    if str[0] == '#':
                        break
                    y2_list.append(float(str))
            min_len = min(len(y1_list), len(y2_list))
            y1, y2 = np.array(y1_list[0:min_len]), np.array(y2_list[0:min_len])
            x = np.linspace(1, min_len, min_len)
            plt.xlabel('frames')
            plt.ylabel('IOU')
            plt.xlim(1, min_len)
            plt.ylim(0, 1)
            plt.plot(x, y1, color='blue', label='with yolo')
            plt.plot(x, y2, color='red', label='without yolo')
        elif mode == 'k_f':
            with open('iou_with_detect.txt', 'r') as fp:
                while True:
                    str = fp.readline()
                    if len(str) == 0:
                        continue
                    if str[0] == '#':
                        break
                    y1_list.append(float(str))
            with open('k_f_75.txt', 'r') as fp:
                while True:
                    str = fp.readline()
                    if len(str) == 0:
                        continue
                    if str[0] == '#':
                        break
                    y2_list.append(float(str))
            with open('k_f_25.txt', 'r') as fp:
                while True:
                    str = fp.readline()
                    if len(str) == 0:
                        continue
                    if str[0] == '#':
                        break
                    y3_list.append(float(str))
            min_len = min(len(y1_list), len(y2_list), len(y3_list))
            y1, y2, y3 = np.array(y1_list[0:min_len]), np.array(y2_list[0:min_len]), np.array(y3_list[0:min_len])
            x = np.linspace(1, min_len, min_len)
            plt.xlabel('frames')
            plt.ylabel('IOU')
            plt.xlim(1, min_len)
            plt.ylim(0, 1)
            plt.plot(x, y1, color='blue', label='period=125 f')
            plt.plot(x, y2, color='red', label='period=75 f', linestyle='-.')
            plt.plot(x, y3, color='green', label='period=25 f', linestyle='--')
        elif mode == 'vs':
            with open('iou_with_detect.txt', 'r') as fp:
                while True:
                    str = fp.readline()
                    if len(str) == 0:
                        continue
                    if str[0] == '#':
                        break
                    y1_list.append(float(str))
            with open('iou_without_detect.txt', 'r') as fp:
                while True:
                    str = fp.readline()
                    if len(str) == 0:
                        continue
                    if str[0] == '#':
                        break
                    y2_list.append(float(str))
            min_len = min(len(y1_list), len(y2_list))
            y1, y2 = np.array(y1_list[0:min_len]), np.array(y2_list[0:min_len])
            x = np.linspace(1, min_len, min_len)
            plt.xlabel('frames')
            plt.ylabel('IOU')
            plt.xlim(1, min_len)
            plt.ylim(0, 1)
            plt.plot(x, y1, color='blue', label='SiamRPN')
            plt.plot(x, y2, color='red', label='KCF')
        else:
            print('Mode wrong. Are u a shit ? ')
            exit

        plt.legend(loc='lower left')
        plt.savefig(name + '.png', dpi=120, bbox_inches='tight')

    def robust(self):
        failure_times = 0
        for ratio in self.iou_list:
            if ratio < self.threshold:
                failure_times += 1
        return failure_times

if __name__ == '__main__':
    tool = criteria_draw([])
    tool.draw_from_file('woman_2', mode='detect')
    
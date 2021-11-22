#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Tuesday, November 26th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import cv2
from matplotlib import pyplot as plt
from matplotlib import animation
import matplotlib.patches as patches
import numpy as np
import os

from core.edge_queue import EdgeQueue
from core.edge_component import EdgeComponent

class VideoPlayer(EdgeComponent):
    def __init__(self, app):
        super().__init__(app, 'player')
    
    def _initialize(self):
        self.render_queue = EdgeQueue(self, "render_queue")
        self.render_list = list()
        pass
    
    def render(self, i):
        
        render_list = []
        try:
            f = self.render_queue.get(timeout=2)
            if type(f) == str:
                self.stop()
                return
            self.logger.info(f"*render frame: {f.frame_property.frame_idx}")
            RGB_img = cv2.cvtColor(f.raw_frame, cv2.COLOR_BGR2RGB)
            self.img.set_array(f.raw_frame)
            render_list.append(self.img)

            for box in f.frame_property.bbox:
                box_id = box.track_id
                if box_id < self.config['max_box']:
                    self.box_buffer[box_id][0].set_xy((box.xmin, box.ymin))
                    self.box_buffer[box_id][0].set_width(box.xmax - box.xmin)
                    self.box_buffer[box_id][0].set_height(box.ymax - box.ymin)
                    self.box_buffer[box_id][1].set_text(box.class_name)
                    self.box_buffer[box_id][1].set_position((box.xmin, box.ymin))
                    render_list.append(self.box_buffer[box_id][0])
                    render_list.append(self.box_buffer[box_id][1])

            for box in f.frame_property.client_bbox:
                box_id = box.track_id
                if box_id < self.config['max_box']:
                    self.client_box_buffer[box_id][0].set_xy((box.xmin, box.ymin))
                    self.client_box_buffer[box_id][0].set_width(box.xmax - box.xmin)
                    self.client_box_buffer[box_id][0].set_height(box.ymax - box.ymin)
                    self.client_box_buffer[box_id][1].set_text(box.class_name)
                    self.client_box_buffer[box_id][1].set_position((box.xmin, box.ymin))
                    render_list.append(self.client_box_buffer[box_id][0])
                    render_list.append(self.client_box_buffer[box_id][1])

        except Exception as e:
            self.logger.info("no more frame")
        return render_list
    
    def handle_close(self, params):
        os._exit(0)

    # render on main thread
    def play(self):
        self.fig, self.ax = plt.subplots(1)
        self.fig.canvas.mpl_connect('close_event', self.handle_close)
        self.img = plt.imshow(np.zeros((self.app.video_streamer.frame_height, self.app.video_streamer.frame_width)))
        self.box_buffer = []
        self.client_box_buffer = []
        cmap = plt.get_cmap("Dark2")
        colors = [cmap(i) for i in np.linspace(0, 1, 3)]
        for i in range(self.config['max_box']):
            box = plt.Rectangle((0, 0), 0, 0, linewidth=2, edgecolor=colors[0], facecolor="none")
            self.ax.add_patch(box)
            text = plt.text(0, 0, '', color="white", verticalalignment="top", bbox={"color": colors[0], "pad": 0})
            self.box_buffer.append([box, text])

        for i in range(self.config['max_box']):
            box = plt.Rectangle((0, 0), 0, 0, linewidth=2, edgecolor=colors[1], facecolor="none")
            self.ax.add_patch(box)
            text = plt.text(0, 0, '', color="white", verticalalignment="top", bbox={"color": colors[1], "pad": 0})
            self.client_box_buffer.append([box, text])

        self.anim = animation.FuncAnimation(self.fig, func=self.render, interval=20)
        # self.anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
        plt.show()
    
    def stop(self):
        self.logger.info("stop animation") 
        self.anim.event_source.stop()
        plt.close()
        

    def run(self):
        pass
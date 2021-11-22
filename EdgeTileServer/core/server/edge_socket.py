#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, November 20th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import threading

from core.edge_queue import EdgeQueue
from utils.json_socket import JsonSocket, SocketType
from core.edge_component import EdgeComponent

class EdgeSocket(EdgeComponent):
    def __init__(self, app):
        super().__init__(app, "socket")
    
    def _initialize(self):
        self.socket = JsonSocket(self.config['ip_addr'], self.config['port'], SocketType.SERVER_MODE, self.logger)
        self.send_queue = EdgeQueue(self, 'send_queue')

    def put_data(self, data):
        self.send_queue.put(data)    

    def run(self):
        self.socket.start()
        if not self.is_init():
            self.logger.error("You should initialize server socket first...")
            return
        while not self.stopped():
            
            obj = self.send_queue.get()
            if obj['frame_id'] == -1:
                self.socket.shutdown()
                break
            status = self.socket.send(obj)
            if status:
                self.logger.info(f"*bbox_send frame: {obj['frame_id']} level: {obj['level']} {obj['group_id']}")
            else:
                self.socket.shutdown()
                # self.app.stop()
                break
        self.logger.info("socket thread exit...")
    
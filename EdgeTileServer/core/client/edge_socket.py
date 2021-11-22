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
        super().__init__(app, 'socket')

    def _initialize(self):
        self.recv_queue = EdgeQueue(self, "recv_queue")
        self.socket = JsonSocket(self.config['ip_addr'], self.config['port'], SocketType.CLIENT_MODE, self.logger)

    def close(self):
        self.socket.shutdown()

    def run(self):
        self.socket.start()
        while not self.stopped():
            try:
                obj = self.socket.recv()
                self.app.cache.update_from_server(obj)
                # self.recv_queue.put(obj)
                self.logger.info(f"*bbox_recv frame: {obj['frame_id']} level: {obj['level']}")
            except:
                break
        self.logger.info("socket thread exit...")
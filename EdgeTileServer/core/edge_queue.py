#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, November 28th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
import queue

class EdgeQueue:
    def __init__(self, app, queue_name, max_size=1):
        super().__init__()
        self.q = queue.Queue()
        self.logger = app.logger
        self.queue_name = queue_name
        self.max_size = max_size
    
    def put(self, obj):
        
        while self.max_size > 0 and self.size() >= self.max_size:
            self.get()

        self.q.put(obj)
        self.logger.info(f"{self.queue_name} size is {self.size()}")
    
    def get(self, block=True, timeout=-1):
        if timeout < 0:
            return self.q.get(block=block)
        else:
            return self.q.get(block=block, timeout=timeout)
    
    def get_nowait(self):
        return self.q.get_nowait()

    def size(self):
        return self.q.qsize()
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, November 21st 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from enum import Enum
import time
import struct
from io import StringIO, BytesIO
import numpy as np
import json
import socket
import logging
import threading


class SocketType(Enum):
    CLIENT_MODE=0,
    SERVER_MODE=1

class JsonSocket:
    def __init__(self, ip, port, socket_type, logger):
        super().__init__()
        self.ip = ip
        self.port = port
        self.type = socket_type
        self.logger = logger.getChild("JsonSocket")
        self.client_socket = None
        self.server_socket = None

    def recv(self):
        # receive the length of the message
        try:
            msg_size = 4
            recv_buffer = b''
            while len(recv_buffer) < msg_size:
                sock_data = self.client_socket.recv(msg_size - len(recv_buffer))
                recv_buffer = recv_buffer + sock_data
            # receive the message
            msg_size = struct.unpack('>i', recv_buffer)[0]
            recv_buffer = b''
            while len(recv_buffer) < msg_size:
                sock_data = self.client_socket.recv(msg_size - len(recv_buffer))
                recv_buffer = recv_buffer + sock_data
            msg = json.loads(str(recv_buffer, encoding='utf-8'))
        except Exception as e:
            self.logger.error("recv message error")
            print(e.args)
            return None
        return msg
    
    def send(self, msg):
        status = True
        try:
            msg_data = json.dumps(msg)
            self.client_socket.sendall(struct.pack('>i', len(msg_data))+ bytes(msg_data, encoding='utf-8'))
        except Exception as e:
            self.logger.error("send message error")
            print(e.args)
            status = False
        return status
    
    def start(self):
        if self.type == SocketType.CLIENT_MODE:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client_socket.connect((self.ip, self.port))
                self.logger.info('Connected to %s on port %s' % (self.ip, self.port))
            except socket.error as e:
                self.logger.info('Connection to %s on port %s failed: %s' % (self.ip, self.port, e))
                
        elif self.type == SocketType.SERVER_MODE:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('', self.port))
            self.logger.info('start listen to {}'.format(self.port))
            self.server_socket.listen(1)
            self.client_socket, client_address = self.server_socket.accept()
            self.logger.info("{0} connect to the server".format(client_address))

    def shutdown(self):
        if self.server_socket:
            try:
                self.server_socket.shutdown(1)
            except Exception as e:
                self.logger.info(e.args)
            try:
                self.server_socket.close()
            except Exception as e:
                self.logger.info(e.args)
        if self.client_socket:
            try:
                self.client_socket.shutdown(1)
            except Exception as e:
                self.logger.info(e.args)
            try:
                self.client_socket.close()
            except Exception as e:
                self.logger.info("Exception as e")

def test_client(logger):
    client_socket = JsonSocket("127.0.0.1", 8090, SocketType.CLIENT_MODE, logger)
    client_socket.start()
    client_socket.send({'a' : 1, 'b': [1, 2, 3]})

def test_server(logger):
    server_socket = JsonSocket("", 8090, SocketType.SERVER_MODE, logger)
    server_socket.start()
    msg = server_socket.recv()
    print(msg)

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('main')
    client_thread = threading.Thread(target=test_client, args=[logger])
    server_thread = threading.Thread(target=test_server, args=[logger])
    server_thread.start()
    time.sleep(2)
    client_thread.start()
    client_thread.join()
    server_thread.join()
    
    print("success.")
   
   
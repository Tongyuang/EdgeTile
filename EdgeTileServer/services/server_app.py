#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Friday, December 6th 2019
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2019 Institute of Trustworthy Network and System, Tsinghua University
'''
from flask import Flask
import threading
import sys
import os
from flask import jsonify
from flask import g


app = Flask(__name__)



def write_server_status(s):
    f = open('data/log/server_status.global', 'w+')
    f.write(str(s))
    f.close()

def get_server_status():
    f = open('data/log/server_status.global', 'r')
    s = int(f.read())
    f.close()
    return s

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/start')
def start_server():
    def start():
        write_server_status(0)
        os.system("python edge_tile_server.py")
        write_server_status(1)
    
    t = threading.Thread(target=start)
    t.start()
    return jsonify({'status': 1})

@app.route('/status')
def server_status():
    s = get_server_status()
    if s:
        return jsonify({'status': 1})
    else:
        return jsonify({'status': 0})


if __name__ == '__main__':
    write_server_status(1)
    app.run(host='0.0.0.0', port=9002)
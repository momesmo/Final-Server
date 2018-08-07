#!/usr/bin/env python3

import sys
import requests
import os
import socket
from flask import jsonify, request, json
import json

ip = ''
port = 2020
size = 1024
global s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def repl():
    while 1:
        command = input("Please enter a command\n")
        if command == 'win':
            s.send(b'{"MSGID": 0, "SOURCE": "Sensor", "DATA": 250}')

if __name__ == '__main__':
    try:
        s.connect((ip, port))

        repl()
    except KeyboardInterrupt:
        s.close()
        print(" - Exiting")

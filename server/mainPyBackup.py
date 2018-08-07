#!/usr/bin/env python3

# for socket connections and HTTP
import sys
import socket
import os
import requests
from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler

host = ''
port = 2000
backlog = 5
size = 1024
app = Flask(__name__)
# global logFile = open('log.txt', 'a')

# initial setup
def setup():
    #request.get_json() in flask to actually get the JSON data
    #flask.jsonify to send JSON data back to the PICs
    global host
    global port
    global backlog
    global size

    # PIC1
    global pic1
    pic1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pic1.bind((host, port))
    pic1.listen(backlog)
    c1, address1 = pic1.accept()
    c1.send(b'{data: pic1}')

def disconnect():
    print("System: exiting")
    pic1.close()

@app.route('/', methods=['GET'])
def index():
    # return flask.jsonify data
    # print to terminal
    # print to file
    print("System: received data from rover")
    return '{c'

@app.route('/send', methods=['POST'])
def send():
    print("System: sending data to rover")
    # receive request from GUI/Client
    input_json = request.get_json(force = True)
    print("Data from client: ")
    print(input_json)
    # logFile.write
    app.logger.info('Command Send Request received from gui client')
    # then send through socket connection to the rover

    return 'sent'

@app.route('/forward', methods=['POST'])
def forward():
    print("System: sending forward command to rover")
    input_json = request.get_json(force = True)
    app.logger.info('Forward command request received from GUI client')
    # send through socket connection to the rover
    return 'forward'

@app.route('/backward', methods=['POST'])
def backward():
    print("System: sending backward command to rover")
    input_json = request.get_json(force = True)
    app.logger.info('Backward command request received from GUI client')
    # send through socket connection to the rover
    return 'backward'

@app.route('/left', methods=['POST'])
def left():
    print("System: sending left command to rover")
    input_json = request.get_json(force = True)
    app.logger.info('Left command request received from GUI client')
    # send through socket connection to the rover
    return 'left'

@app.route('/right', methods=['POST'])
def right():
    print("System: sending right command to rover")
    input_json = request.get_json(force = True)
    app.logger.info('Right command request received from GUI client')
    # send through socket connection to the rover
    return 'right'

try:
    if __name__ == "__main__":
        # setup()
        print("System: server running")
        formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
        handler = RotatingFileHandler('server.log', maxBytes=10000000, backupCount=5)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.run(host = '0.0.0.0', port = 80, debug = True)

except KeyboardInterrupt:
    # logFile.close()
    disconnect()

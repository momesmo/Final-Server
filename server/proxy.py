#!/usr/bin/env python3

import sys
import requests
import os
import socket
import json
from _thread import *
import threading
import queue
from flask import request, jsonify, json
from IR_graph import getThresholdData
from RGB_graph import getThresholdData as get_RGB_Thresholds


print_lock = threading.Lock()

# JSON keys and values for Rovers as follows:
# {'MSG_TYPE': i, 'MSG_ID':#, 'COMMAND':_}

# For saving data to txt database
MAX_ENCODER_DATA = 200
x = 0
xdata = []
ydata_left = []
ydata_right = []
FILE_NAME = 'a.txt'
IR_DATA_FILE = 'IR_data.txt'
RGB_DATA_FILE = 'RGB_data.txt'


def get_IR_Thresholds():
    return getThresholdData()

def update_IR_Data(raw_data):
    #empty the file
    open(IR_DATA_FILE, 'w').close()
    #write new data to the file
    with open(IR_DATA_FILE, 'w') as f:
        f.write(str(raw_data))

def update_RGB_Data(r, g, b):
    #empty the file
    open(RGB_DATA_FILE, 'w').close()
    #write new data to the file
    with open(RGB_DATA_FILE, 'w') as f:
        f.write(str(r))
        f.write('\n')
        f.write(str(g))
        f.write('\n')
        f.write(str(b))

    
def update_data(left_x, right_x):
    global x, xdata, ydata_left, ydata_right
    if len(xdata) > MAX_ENCODER_DATA:
        ydata_left = ydata_left[1:]
        ydata_right = ydata_right[1:]
    else:
        xdata.append(x)
        x += 1
    ydata_left.append(left_x)
    ydata_right.append(right_x)
    with open(FILE_NAME, 'w') as f:
        f.write(" ".join(str(x) for x in xdata))
        f.write('\n')
        f.write(" ".join(str(x) for x in ydata_left))
        f.write('\n')
        f.write(" ".join(str(x) for x in ydata_right))
        f.write('\n')

def find_values(id, json_rep):
    if type(json_rep) == str:
        json_rep = json.loads(json_rep)
    if type(json_rep) is dict:
        for jsonkey in json_rep:
            if type(json_rep[id]) in (list, dict):
                get_all(json_rep[jsonkey], id)
            elif jsonkey == id:
                return json_rep[jsonkey]

def is_json(str):
    try:
        json_obj = json.loads(str)
    except ValueError:
        return False
    return True

def tsafe_print(string):
    print_lock.acquire()
    print(string)
    print_lock.release()

def rover_pic():
    # accepts the connection
    global roverC, roverAdd
    roverC, roverAdd = s1.accept()
    tsafe_print("Accepted connection from Rover")
    while True:
        roverData = roverC.recv(size)
        if(roverData or not roverMQ.empty()):
            if not roverMQ.empty():
                toSend = roverMQ.get()
                roverC.send(toSend.encode())
                tsafe_print("Sent command %s to Rover\n" % toSend)
            if roverData == b'{s}':
                #roverC.send(b'{GO}')
                tsafe_print("GO Rover")
            # Got a correctly formatted JSON payload from rover
            elif( is_json(roverData.decode('utf-8')) == True):
                newS = roverData.decode('utf-8')
                jrep = json.loads(newS)
                if jrep.get("ERROR", None) is not None:
                    tsafe_print("Error Detected from Rover!\n\n")
                elif jrep["SOURCE"] == "Motor":
                    msgID = jrep["MSGID"]
                    # Construct the response
                    # tsafe_print("Rover data: %s\n" % newS)
                    #roverC.send(b'{"MSG_TYPE": 0, "MSG_ID": %d, "COMMAND": "test"}' % int(msgID))
                    #tsafe_print("Sending ACK for Motor msg: %d" % int(msgID))
                    try:
                        update_data(jrep["LEFT"], jrep["RIGHT"])
                    except:
                        print("Update Fail")
                elif jrep["SOURCE"] == "Sensor":
                    #receive RGB raw data here
                    msgID = jrep["MSGID"]
                    # Construct the response
                    #tsafe_print("Rover data: %s\n" % newS)
                    try:
                        update_RGB_Data(jrep["R"], jrep["G"], jrep["B"])
                    except:
                        print("Update Fail")
                    #TODO: copy below here to elif jrep["SOURCE"]
                    high_threshold, low_threshold = get_RGB_Thresholds()
                    msg = b''
                    if low_threshold[0] < jrep["R"] and jrep["R"] < high_threshold[0] and low_threshold[2] < jrep["G"] and jrep["G"] < high_threshold[2] and low_threshold[4] < jrep["B"] and jrep["B"] < high_threshold[4]:
                        #Sees red
                        tsafe_print("RGB Sensor: Red")
                        msg = b'RED'
                    elif low_threshold[6] < jrep["R"] and jrep["R"] < high_threshold[6] and low_threshold[8] < jrep["G"] and jrep["G"] < high_threshold[8] and low_threshold[10] < jrep["B"] and jrep["B"] < high_threshold[10]:
                        #sees green
                        tsafe_print("RGB Sensor: Green")
                        msg = b'GREEN'
                    elif low_threshold[12] < jrep["R"] and jrep["R"] < high_threshold[12] and low_threshold[14] < jrep["G"] and jrep["G"] < high_threshold[14] and low_threshold[16] < jrep["B"] and jrep["B"] < high_threshold[16]:
                        #sees blue
                        tsafe_print("RGB Sensor: Blue")
                        msg = b'BLUE'
                    elif low_threshold[18] < jrep["R"] and jrep["R"] < high_threshold[18] and low_threshold[20] < jrep["G"] and jrep["G"] < high_threshold[20] and low_threshold[22] < jrep["B"] and jrep["B"] < high_threshold[22]:
                        #sees black
                        tsafe_print("RGB Sensor: Black")
                        msg = b'BLACK'
                    winSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    winSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    winSockPort = 2060
                    winSock.connect(('', winSockPort))
                    winSock.send(msg)
                    winSock.close()

            # NOT correctly formatted JSON payload from rover
            else:
                newS = roverData.decode('utf-8')
                tempList = []
                for i in newS.split("}"):
                    i += "}"
                    tempList.append(i)
                for item in tempList:
                    if is_json(item):
                        #tsafe_print("Rover data: %s\n" % item)
                        jrep = json.loads(item)
                        if jrep["SOURCE"] == "Motor":
                            msgID = jrep["MSGID"]
                            #roverC.send(b'{"MSG_TYPE": 0, "MSG_ID": %d, "COMMAND": "test"}' % int(msgID))
                            #tsafe_print("Sending ACK for Motor msg: %d" % int(msgID))
                            try:
                                update_data(jrep["LEFT"], jrep["RIGHT"])
                            except:
                                print("Update Fail")
                            # Check to see if any messages in the roverMQ to be sent
                        elif jrep["SOURCE"] == "Sensor":
                            #receive RGB raw data here
                            msgID = jrep["MSGID"]
                            # Construct the response
                            #tsafe_print("Rover data: %s\n" % newS)
                            try:
                                update_RGB_Data(jrep["R"], jrep["G"], jrep["B"])
                            except:
                                print("Update Fail")
                            #TODO: copy below here to elif jrep["SOURCE"]
                            high_threshold, low_threshold = get_RGB_Thresholds()
                            msg = b''
                            if low_threshold[0] < jrep["R"] and jrep["R"] < high_threshold[0] and low_threshold[2] < jrep["G"] and jrep["G"] < high_threshold[2] and low_threshold[4] < jrep["B"] and jrep["B"] < high_threshold[4]:
                                #Sees red
                                tsafe_print("RGB Sensor: Red")
                                msg = b'RED'
                            elif low_threshold[6] < jrep["R"] and jrep["R"] < high_threshold[6] and low_threshold[8] < jrep["G"] and jrep["G"] < high_threshold[8] and low_threshold[10] < jrep["B"] and jrep["B"] < high_threshold[10]:
                                #sees green
                                tsafe_print("RGB Sensor: Green")
                                msg = b'GREEN'
                            elif low_threshold[12] < jrep["R"] and jrep["R"] < high_threshold[12] and low_threshold[14] < jrep["G"] and jrep["G"] < high_threshold[14] and low_threshold[16] < jrep["B"] and jrep["B"] < high_threshold[16]:
                                #sees blue
                                tsafe_print("RGB Sensor: Blue")
                                msg = b'BLUE'
                            elif low_threshold[18] < jrep["R"] and jrep["R"] < high_threshold[18] and low_threshold[20] < jrep["G"] and jrep["G"] < high_threshold[20] and low_threshold[22] < jrep["B"] and jrep["B"] < high_threshold[22]:
                                #sees black
                                tsafe_print("RGB Sensor: Black")
                                msg = b'BLACK'
                            winSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            winSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            winSockPort = 2060
                            winSock.connect(('', winSockPort))
                            winSock.send(msg)
                            winSock.close()


        if not roverData:
            # Check to see if any messages in the roverMQ to be sent
            tsafe_print("Lost connection to ROVER\n")
            roverC.close()
            roverC, roverAdd = s1.accept()
            tsafe_print("Reconnected to ROVER\n")
            roverC.send(b'{GO}')

def observer_pic():
    global observeC, observeAdd
    observeC, observeAdd = s2.accept()
    tsafe_print("Accepted connection from Observer")
    while True:
        observeData = observeC.recv(size)
        if( observeData or not observerMQ.empty() ):
            if not observerMQ.empty():
                toSend = observerMQ.get()
                observerC.send(toSend.encode())
                tsafe_print("Sent command %s to Observer" % toSend)
            if observeData == b'{s}':
                observeC.send(b'{GO}')
            elif( is_json(observeData.decode('utf-8')) == True):
                newS = observeData.decode('utf-8')
                tsafe_print("Observer data: %s\n" % newS)
                jrep = json.loads(newS)
                if jrep.get("ERROR", None) is not None:
                    tsafe_print("Error Detected from Observer!\n\n")
                else:
                    if (jrep["SOURCE"] == "Sensor"):
                        high, low = get_IR_Thresholds()
                        update_IR_Data(jrep["DATA"])
                        if (jrep["DATA"] >= low and jrep["DATA"] <= high):
                            # Waiting for rover to finish
                            # tsafe_print("IR Sensor sees the wall")
                            dummy = 0
                        elif (jrep["DATA"] < low):
                            # Error
                            tsafe_print("IR Sensor error has occured")
                        elif (jrep["DATA"] > high):
                            # Rover has crossed finish line
                            tsafe_print("Rover has crossed the IR sensor")
                            winSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            winSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            winSockPort = 2060
                            winSock.connect(('', winSockPort))
                            winSock.send(b'WIN')
                            winSock.close()

                        else:
                            #should never get here
                            tsafe_print("Got some funky data")
                    msgID = jrep["MSGID"]
                    # Construct the response
                    observeC.send(b'{"MSG_TYPE": 0, "MSG_ID": %d, "COMMAND": "test"}' % int(msgID))
                    # Check to see if there are any commands in observerMQ to be sent
            else:
                # Check to see if there are any commands in observerMQ to be sent
                newS = observeData.decode('utf-8')
                tempList = []
                for i in newS.split("}"):
                    i += "}"
                    tempList.append(i)
                for item in tempList:
                    if is_json(item):
                        tsafe_print("Observer data: %s\n" % item)
                        # then send the response
                        jrep = json.loads(item)
                        msgID = jrep["MSGID"]
                        observeC.send(b'{"MSG_TYPE": 0, "MSG_ID": %d, "COMMAND": "test"}' % int(msgID))

        if not observeData:
            tsafe_print("Lost connection to OBSERVER\n")
            observeC.close()
            observeC, observeAdd = s2.accept()
            tsafe_print("Reconnected to OBSERVER\n")
            observeC.send(b'{GO}')

def gui():
    global guiC, guiAdd
    guiC, guiAdd = s3.accept()
    tsafe_print("Accepted connection from GUI Client")
    while True:
        guiCommand = guiC.recv(size)
        if guiCommand:
            if( is_json(guiCommand.decode('utf-8')) == True):
                newS = guiCommand.decode('utf-8')
                tsafe_print("GUI command: %s\n" % newS)
                jrep = json.loads(newS)
                if( jrep["TARGET"] == "Rover"):
                    # Rover Commands
                    # Put command in roverMQ
                    roverMQLock.acquire()
                    # Determine what the command is
                    # Put correct JSON format in the queue
                    if (jrep["COMMAND"] == "f"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 1}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "b"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 2}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "l"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 3}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "r"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 4}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "s"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 5}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "littleL"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 6}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "littleR"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 7}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "60"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 8}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "80"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 9}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "s1"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 10}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "s2"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 11}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "s3"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 12}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "s4"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 13}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "s5"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 14}'
                        roverMQ.put(mess)
                    elif( jrep["COMMAND"] == "s6"):
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 15}'
                        roverMQ.put(mess)
                    # SETTING PI VARIALBLES FOR LEFT AND RIGHT
                    elif jrep["COMMAND"] == "lefti":
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 90, "VALUE": %d}' % jrep["VALUE"]
                        roverMQ.put(mess)
                    elif jrep["COMMAND"] == "leftp":
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 80, "VALUE": %d}' % jrep["VALUE"]
                        roverMQ.put(mess)
                    elif jrep["COMMAND"] == "righti":
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 91, "VALUE": %d}' % jrep["VALUE"]
                        roverMQ.put(mess)
                    elif jrep["COMMAND"] == "rightp":
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 81, "VALUE": %d}' % jrep["VALUE"]
                        roverMQ.put(mess)
                    elif jrep["COMMAND"] == "rightd":
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 71, "VALUE": 0}'
                        roverMQ.put(mess)
                    elif jrep["COMMAND"] == "leftd":
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 70, "VALUE": 0}'
                        roverMQ.put(mess)
                    elif jrep["COMMAND"] == "init":
                        mess = '{"MSG_TYPE": 1, "MSG_ID": 0, "COMMAND": 99, "VALUE": 0}'
                        roverMQ.put(mess)
                    else:
                        tsafe_print("Received incorrect command from GUI client")
                    roverMQLock.release()

                elif( jrep["TARGET"] == "Observer"):
                    # Observer Commands
                    # Put in observerMQ
                    observerMQLock.acquire()
                    # Determine what the command is
                    # Put correct JSON format in the queue
                    observerMQLock.release()

                elif( jrep["TARGET"] == "Server"):
                    if( jrep["COMMAND"] == "get" ):
                        ip = 'http://localhost:4000/'
                        r = requests.get(ip)
                        print(r.json())
                        backToClient = json.dumps(r.json())
                        guiC.send(backToClient.encode())
                    elif( jrep["COMMAND"] == "post" ):
                        name = jrep["NAME"]
                        score = jrep["SCORE"]
                        ip = 'http://localhost:4000/'
                        r = requests.post(ip, data={'name': name, 'score': score})

        if not guiCommand:
            tsafe_print("Lost connection to GUI Client")
            guiC.close()
            guiC, guiAdd = s3.accept()
            tsafe_print("Reconnected to GUI\n")

def main():
    try:
        port1 = 2000
        port2 = 2020
        port3 = 2040
        backlog = 5
        global size
        size = 1024
        host = ''

        global s1
        global s2
        global s3
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s1.bind((host, port1))
        s2.bind((host, port2))
        s3.bind((host, port3))
        s1.listen(5)
        s2.listen(5)
        s3.listen(5)
        print("Sockets are listening")

        global roverMQ
        global roverMQLock
        roverMQLock = threading.Lock()
        roverMQ = queue.Queue(maxsize=0)
        global observerMQ
        global observerMQLock
        observerMQLock = threading.Lock()
        observerMQ = queue.Queue(maxsize=0)

        # Loop forever until client wishes to exit
        t1 = threading.Thread(target=rover_pic)
        t2 = threading.Thread(target=observer_pic)
        t3 = threading.Thread(target=gui)
        t1.start()
        t2.start()
        t3.start()

    except KeyboardInterrupt:
        t1.join()
        t2.join()
        t3.join()
        roverC.shutdown(socket.SHUT_RDWR)
        roverC.close()
        observeC.shutdown(socket.SHUT_RDWR)
        observeC.close()
        s.close()

if __name__ == '__main__':
    main()

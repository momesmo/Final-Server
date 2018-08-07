#!/usr/bin/env python3

import sys
import requests
import os
import socket
import threading
from flask import jsonify, request, json
import json

from IR_graph import getThresholdData as getIRT
from RGB_graph import getThresholdData as getRGBT

ip = ''
port = 2040
size = 1024
global s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

port2 = 2060
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s2.bind((ip, port2))
s2.listen(5)

def dummy():
    dumC, dumA = s2.accept()
    while 1:
        dumb = dumC.recv(size)

def repl():
    while 1:
        command = input("Please enter a command\n")
        if command == 'guif' or command == 'w':
            s.send(b'{"TARGET": "Rover", "COMMAND": "f"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "f"}')
        elif command == 'guib' or command == 's':
            s.send(b'{"TARGET": "Rover", "COMMAND": "b"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "b"}')
        elif command == 'guil' or command == 'a':
            s.send(b'{"TARGET": "Rover", "COMMAND": "l"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "l"}')
        elif command == 'guir' or command == 'd':
            s.send(b'{"TARGET": "Rover", "COMMAND": "r"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "r"}')
        elif command == 'guis' or command == 'speed0' or command == 'q':
            s.send(b'{"TARGET": "Rover", "COMMAND": "s"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "s"}')
        elif command == 'z':
            s.send(b'{"TARGET": "Rover", "COMMAND": "littleL"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "littleL"}')
        elif command == 'c':
            s.send(b'{"TARGET": "Rover", "COMMAND": "littleR"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "littleR"}')
        elif command == 'gui60':
            s.send(b'{"TARGET": "Rover", "COMMAND": "60"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "60"}')
        elif command == 'gui80':
            s.send(b'{"TARGET": "Rover", "COMMAND": "80"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "80"}')
        elif command == 'speed1':
            s.send(b'{"TARGET": "Rover", "COMMAND": "s1"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "s1"}')
        elif command == 'speed2':
            s.send(b'{"TARGET": "Rover", "COMMAND": "s2"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "s2"}')            
        elif command == 'speed3':
            s.send(b'{"TARGET": "Rover", "COMMAND": "s3"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "s3"}')            
        elif command == 'speed4':
            s.send(b'{"TARGET": "Rover", "COMMAND": "s4"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "s4"}')            
        elif command == 'speed5':
            s.send(b'{"TARGET": "Rover", "COMMAND": "s5"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "s5"}')            
        elif command == 'speed6':
            s.send(b'{"TARGET": "Rover", "COMMAND": "s6"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "s6"}')
    # SETTING SET_VEL
        elif command[0:6] == 'setvel':
            try:
                x = int(command[6:])
                if x < 0 or x > 90:
                    raise ValueError()
                s.send(b'{"TARGET": "Rover", "COMMAND": "setvel", "VALUE": %d}' % x)
                print('Sent {"TARGET": "Rover", "COMMAND": "setvel", "VALUE": %d}' % x)
            except:
               print('Invalid formatting. \'setvel\' should be followed by a positive integer.\n')
    # SETTING PI VARIABLES FOR LEFT AND RIGHT
        elif command[0:5] == 'lefti':
            try:
                x = int(command[5:])
                if x < 0:
                    raise ValueError()
                s.send(b'{"TARGET": "Rover", "COMMAND": "lefti", "VALUE": %d}' % x)
                print('Sent {"TARGET": "Rover", "COMMAND": "lefti", "VALUE": %d}' % x)
            except:
               print('Invalid formatting. \'lefti\' should be followed by a positive integer.\n')
        elif command[0:5] == 'leftp':
            try:
                x = int(command[5:])
                if x < 0:
                    raise ValueError()
                s.send(b'{"TARGET": "Rover", "COMMAND": "leftp", "VALUE": %d}' % x)
                print('Sent {"TARGET": "Rover", "COMMAND": "leftp", "VALUE": %d}' % x)
            except:
               print('Invalid formatting. \'leftp\' should be followed by a positive integer.\n')
        elif command[0:5] == 'leftd':
            try:
                x = int(command[5:])
                if x < 0:
                    raise ValueError()
                s.send(b'{"TARGET": "Rover", "COMMAND": "leftd", "VALUE": %d}' % x)
                print('Sent {"TARGET": "Rover", "COMMAND": "leftd", "VALUE": %d}' % x)
            except:
               print('Invalid formatting. \'leftd\' should be followed by a positive integer.\n')       
        elif command[0:6] == 'righti':
            try:
                x = int(command[6:])
                if x < 0:
                    raise ValueError()
                s.send(b'{"TARGET": "Rover", "COMMAND": "righti", "VALUE": %d}' % x)
                print('Sent {"TARGET": "Rover", "COMMAND": "righti", "VALUE": %d}' % x)
            except:
               print('Invalid formatting. \'righti\' should be followed by a positive integer.\n')
        elif command[0:6] == 'rightp':
            try:
                x = int(command[6:])
                if x < 0:
                    raise ValueError()
                s.send(b'{"TARGET": "Rover", "COMMAND": "rightp", "VALUE": %d}' % x)
                print('Sent {"TARGET": "Rover", "COMMAND": "rightp", "VALUE": %d}' % x)
            except:
               print('Invalid formatting. \'rightp\' should be followed by a positive integer.\n')
        elif command[0:6] == 'rightd':
            try:
                x = int(command[6:])
                if x < 0:
                    raise ValueError()
                s.send(b'{"TARGET": "Rover", "COMMAND": "rightd", "VALUE": %d}' % x)
                print('Sent {"TARGET": "Rover", "COMMAND": "rightd", "VALUE": %d}' % x)
            except:
               print('Invalid formatting. \'rightd\' should be followed by a positive integer.\n')
        elif command == 'init':
            s.send(b'{"TARGET": "Rover", "COMMAND": "init"}')
            print('Sent {"TARGET": "Rover", "COMMAND": "init"}')
        elif command == 'man':
            print('gui[f,b,l,r,s] for movement\nsetVel[#] for changing velocity\n[left,right][p,i,d][#] for changing L/R PID variables')
        

        elif command == 'rget':
            # ip = 'http://localhost:4000/'
            # r = requests.get(ip)
            # print(r.json())
            string = '{"TARGET": "Server", "COMMAND": "get"}'
            s.send(string.encode('utf-8'))
            response = s.recv(size)
            print(response.decode('utf-8'))

        elif command == 'rpost':
            name = input("What name would you like to post? ")
            score = input("What score would you like to post? ")
            # ip = 'http://localhost:4000/'
            # r = requests.post(ip, data={'name': name, 'score': score})
            payload = '{"TARGET": "Server", "COMMAND": "post", "NAME": "%s", "SCORE": "%s"}' % (name, score)
            print(payload)
            s.send(payload.encode('utf-8'))
            
        elif command == 'Change_IR_Threshold':
            high, low = getIRT()
            print('Current Thresholds:\nHigh = ', high, '\nLow = ', low)
            newHigh = input("High = ")
            newLow = input("Low = ")
            open('IR_thresholds.txt', 'w').close()
            with open('IR_thresholds.txt', 'w') as f:
                f.write(newHigh)
                f.write('\n')
                f.write(newLow)
            
        elif command == 'Change_RGB_Threshold':
            high, low = getRGBT()
            
            print('Current Red Thresholds:\nRed_HighR = ', high[0])
            print('Red_LowR = ', low[0])
            print('Red_HighG = ', high[2])
            print('Red_LowG = ', low[2])
            print('Red_HighB = ', high[4])
            print('Red_LowB = ', low[4])
            print()
            newRed_HighR = input('Red_HighR = ')
            newRed_LowR = input('Red_LowR = ')
            newRed_HighG = input('Red_HighG = ')
            newRed_LowG = input('Red_LowG = ')
            newRed_HighB = input('Red_HighB = ')
            newRed_LowB = input('Red_LowB = ')
            print()

            print('Current Green Thresholds:\nGreen_HighR = ', high[6])
            print('Green_LowR = ', low[6])
            print('Green_HighG = ', high[8])
            print('Green_LowG = ', low[8])
            print('Green_HighB = ', high[10])
            print('Green_LowB = ', low[10])
            print()
            newGreen_HighR = input('Green_HighR = ')
            newGreen_LowR = input('Green_LowR = ')
            newGreen_HighG = input('Green_HighG = ')
            newGreen_LowG = input('Green_LowG = ')
            newGreen_HighB = input('Green_HighB = ')
            newGreen_LowB = input('Green_LowB = ')
            print()

            print('Current Blue Thresholds:\nBlue_HighR = ', high[12])
            print('Blue_LowR = ', low[12])
            print('Blue_HighG = ', high[14])
            print('Blue_LowG = ', low[14])
            print('Blue_HighB = ', high[16])
            print('Blue_LowB = ', low[16])
            print()
            newBlue_HighR = input('Blue_HighR = ')
            newBlue_LowR = input('Blue_LowR = ')
            newBlue_HighG = input('Blue_HighG = ')
            newBlue_LowG = input('Blue_LowG = ')
            newBlue_HighB = input('Blue_HighB = ')
            newBlue_LowB = input('Blue_LowB = ')
            print()

            print('Current Brown Thresholds:\nBrown_HighR = ', high[18])
            print('Brown_LowR = ', low[18])
            print('Brown_HighG = ', high[20])
            print('Brown_LowG = ', low[20])
            print('Brown_HighB = ', high[22])
            print('Brown_LowB = ', low[22])
            print()
            newBrown_HighR = input('Brown_HighR = ')
            newBrown_LowR = input('Brown_LowR = ')
            newBrown_HighG = input('Brown_HighG = ')
            newBrown_LowG = input('Brown_LowG = ')
            newBrown_HighB = input('Brown_HighB = ')
            newBrown_LowB = input('Brown_LowB = ')
            print()
            l_high = [newRed_HighR, newRed_HighG, newRed_HighB, newGreen_HighR, newGreen_HighG, newGreen_HighB, newBlue_HighR, newBlue_HighG, newBlue_HighB, newBrown_HighR, newBrown_HighG, newBrown_HighB]
            l_low = [newRed_LowR, newRed_LowG, newRed_LowB, newGreen_LowR, newGreen_LowG, newGreen_LowB, newBlue_LowR, newBlue_LowG, newBlue_LowB, newBrown_LowR, newBrown_LowG, newBrown_LowB]
                
            #write values twice to txt file
            count = 0
            open('RGB_thresholds.txt', 'w').close()
            with open('RGB_thresholds.txt', 'w') as f:
                for each in l_high:
                    count += 1
                    f.write(str(int(each)*1000))
                    f.write(' ')
                    f.write(str(int(each)*1000))
                    if count < 12:
                        f.write(' ')
                    else:
                        f.write('\n')
                        
                count = 0
                for each in l_low:
                    count += 1
                    f.write(str(int(each)*1000))
                    f.write(' ')
                    f.write(str(int(each)*1000))
                    if count < 12:
                        f.write(' ')

        else:
            print("Invalid command. Options are guif, guib, guil, guir, guis, rget, rpost, Change_IR_Threshold, and Change_RGB_Threshold.\n")

if __name__ == '__main__':
    try:
        s.connect((ip, port))
        t1 = threading.Thread(target=repl)
        t2 = threading.Thread(target=dummy)
        t1.start()
        t2.start()

    except KeyboardInterrupt:
        t1.join()
        t2.join()

        s.close()
        s2.close()
        print(" - Exiting")

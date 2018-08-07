#!/usr/bin/env python3

import sys
import requests
import os
import socket
from flask import jsonify, request, json
import threading
import queue

#for Qt Stuff
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

ip = ''
size = 1024
port = 2040
global s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.connect((ip, port))

port2 = 2060
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s2.bind((ip, port2))
s2.listen(5)

global pauseButtonState
pauseButtonState = True

global displayState
displayState = 'init'

global gameTime
gameTime = 0

global finalScore
finalScore = 0

global boardString
boardString = ''

global winMQ, win_queue_lock
winMQ = queue.Queue(maxsize=0)
win_queue_lock = threading.Lock()

global lastMotorMoveCommand
lastMotorMoveCommand = ""

global winCondition
winCondition = False

global lastState
lastState = ""

def winReceive():
    global s2, winMQ, win_queue_lock, gameTime, winCondition, lastMotorMoveCommand, displayState, lastState
    proxyC, proxyAdd = s2.accept()
    while True:
        fromProxy = proxyC.recv(size)
        if(fromProxy):
            #print("Data received from proxy:")
            #print("%s" % fromProxy)
            if (fromProxy == b'WIN' and winCondition == False):
                win_queue_lock.acquire()
                winMQ.put('WIN')
                s.send(b'{"TARGET": "Rover", "COMMAND": "s"}')
                winCondition = True
                win_queue_lock.release()
            elif fromProxy == b'RED':
                #bad timer gate
                if lastState != 'R':
                    lastState = 'R'
                    gameTime += 5
                    print("Red +5")
            elif fromProxy == b'GREEN':
                #good timer gate
                if lastState != 'G':
                    lastState = 'G'
                    gameTime -= 5
                    print("Green -5")
            elif fromProxy == b'BLUE':
                #point booster, slight timer decrease
                if lastState != 'B':
                    lastState = 'B'
                    gameTime -= 1
                    print("Blue -1")
            elif fromProxy == b'BLACK':
                if displayState == 'game':
                    win_queue_lock.acquire()
                    winMQ.put('LOSE')
                    s.send(b'{"TARGET": "Rover", "COMMAND": "s"}')
                    win_queue_lock.release()
                    print("BLACK YOU LOSE")

        if not fromProxy:
            proxyC.close()
            proxyC, proxyAdd = s2.accept()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'The aMAZEing Race'
        self.left = 100
        self.top = 100
        self.width = 300
        self.height = 180

        self.layout = QGridLayout()
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.initUI()
        self.show()

    def initUI(self):
        # Main menu UI
        global displayState
        displayState = 'init'
        self.playButton = QPushButton('Play', self)
        self.playButton.setToolTip('Play the aMAZEing Race!')
        self.playButton.clicked.connect(self.play_on_click)

        self.leaderButton = QPushButton('Leader Board', self)
        self.leaderButton.setToolTip('Checkout the Leaderboards')
        self.leaderButton.clicked.connect(self.leader_on_click)

        self.debugMotor = QPushButton('Debug Motor', self)
        self.debugMotor.setToolTip('Observe Motor Encoder Data')
        self.debugMotor.clicked.connect(self.debug_motor_click)

        self.debugSensor = QPushButton('Debug IR Sensor', self)
        self.debugSensor.setToolTip('Observe IR Sensor Data')
        self.debugSensor.clicked.connect(self.debug_ir_click)

        self.debugRGBSensor = QPushButton('Debug RGB Sensor', self)
        self.debugRGBSensor.setToolTip('Observe RGB Sensor Data')
        self.debugRGBSensor.clicked.connect(self.debug_rgb_click)

        self.layout.addWidget(self.playButton, 0, 0)
        self.layout.addWidget(self.leaderButton, 0, 2)
        self.layout.addWidget(self.debugMotor, 2, 1)
        self.layout.addWidget(self.debugSensor, 3, 1)
        self.layout.addWidget(self.debugRGBSensor, 4, 1)

    def gameUI(self):
        # The actual game UI
        global displayState
        displayState = 'game'
        self.wButton = QPushButton('Forward', self)
        self.wButton.setToolTip('Press to Move Forward')
        self.wButton.pressed.connect(self.w_on_click)
        self.wButton.setFixedSize(100, 60)

        self.cButton = QRadioButton(self)

        self.aButton = QPushButton('Left', self)
        self.aButton.setToolTip('Press to Move Left')
        self.aButton.pressed.connect(self.a_on_click)
        self.aButton.setFixedSize(100, 60)

        self.sButton = QPushButton('Back', self)
        self.sButton.setToolTip('Press to Move Backward')
        self.sButton.pressed.connect(self.s_on_click)
        self.sButton.setFixedSize(100, 60)

        self.dButton = QPushButton('Right', self)
        self.dButton.setToolTip('Press to Move Right')
        self.dButton.pressed.connect(self.d_on_click)
        self.dButton.setFixedSize(100, 60)

        self.smallRightButton = QPushButton('Small Right', self)
        self.smallRightButton.setToolTip('Press to make small adjustment right')
        self.smallRightButton.pressed.connect(self.small_r_click)
        self.smallRightButton.setFixedSize(100, 60)

        self.smallLeftButton = QPushButton('Small Left', self)
        self.smallLeftButton.setToolTip('Press to make small adjustment left')
        self.smallLeftButton.pressed.connect(self.small_l_click)
        self.smallLeftButton.setFixedSize(100, 60)

        self.stopButton = QPushButton('Halt', self)
        self.stopButton.setToolTip('Stop rover movement')
        self.stopButton.pressed.connect(self.halt_on_click)
        self.stopButton.setFixedSize(100, 60)

        self.label = QLabel('Play clock: %d' % gameTime, self)
        self.label.setToolTip('Play Clock')
        self.label.setStyleSheet("background-color: gray")
        self.label.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton('Back', self)
        self.backButton.setToolTip('Go back to menu')
        self.backButton.pressed.connect(self.back_on_click)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_display)
        self.timer.setSingleShot(False)

        tempString = ''
        if(pauseButtonState == True):
            tempString = 'Pause'
        else:
            tempString = 'Play'
        self.pauseButton = QPushButton(tempString, self)
        self.pauseButton.setToolTip('Pause game clock')
        self.pauseButton.clicked.connect(self.pause_on_click)

        self.layout.addWidget(self.wButton, 1, 1)
        self.layout.addWidget(self.cButton, 1, 0)
        self.layout.addWidget(self.aButton, 2, 0)
        self.layout.addWidget(self.smallLeftButton, 3, 0)
        self.layout.addWidget(self.sButton, 3, 1)
        self.layout.addWidget(self.dButton, 2, 2)
        self.layout.addWidget(self.smallRightButton, 3, 2)
        self.layout.addWidget(self.stopButton, 2, 1)
        self.layout.addWidget(self.label, 5, 0, 2, 3)
        self.layout.addWidget(self.backButton, 7, 0)
        self.layout.addWidget(self.pauseButton, 7, 2)

        if not pauseButtonState:
            self.wButton.setEnabled(False)
            self.aButton.setEnabled(False)
            self.smallLeftButton.setEnabled(False)
            self.sButton.setEnabled(False)
            self.dButton.setEnabled(False)
            self.smallRightButton.setEnabled(False)
            self.stopButton.setEnabled(False)
        else:
            self.wButton.setEnabled(True)
            self.aButton.setEnabled(True)
            self.smallLeftButton.setEnabled(True)
            self.sButton.setEnabled(True)
            self.dButton.setEnabled(True)
            self.smallRightButton.setEnabled(True)
            self.stopButton.setEnabled(True)


        self.timer.start(1000)

    def leaderBoardUI(self):
        # Leaderboard Display
        global displayState
        displayState = 'leader'
        self.board = QTextEdit(self)
        self.board.setPlainText(boardString)
        self.board.setReadOnly(True)

        self.backButton = QPushButton('Back', self)
        self.backButton.setToolTip('Go back to menu')
        self.backButton.clicked.connect(self.back_on_click)

        self.layout.addWidget(self.board, 0, 0, 2, 3)
        self.layout.addWidget(self.backButton, 2, 1)

    def victoryUI(self):
        global displayState
        displayState = 'win'
        self.label1 = QLabel('Name:')
        self.label2 = QLabel('Score: %d' % finalScore)
        self.label2.setStyleSheet("background-color: gray")
        self.label2.setAlignment(Qt.AlignCenter)

        self.edit = QLineEdit(self)

        self.backButton = QPushButton('Submit', self)
        self.backButton.setToolTip('Submit and go back to menu')
        self.backButton.clicked.connect(self.submit_on_click)

        self.layout.addWidget(self.label1, 0, 0)
        self.layout.addWidget(self.edit, 0, 1, 1, 2)
        self.layout.addWidget(self.label2, 1, 0, 1, 3)
        self.layout.addWidget(self.backButton, 2, 1)

    def loseUI(self):
        global displayState
        displayState = 'lose'
        self.label = QLabel('You hit a wall and lost! Please reset the Rover and try again.')
        self.label.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton('Menu', self)
        self.backButton.setToolTip('Go back to the main menu')
        self.backButton.clicked.connect(self.back_on_click)

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.backButton, 1, 0)

    @pyqtSlot()
    def update_time_display(self):
        global gameTime, pauseButtonState, displayState, winMQ, finalScore
        if( pauseButtonState == True):
            gameTime += 1
        if(displayState == 'game'):
            self.label.setText('Play clock: %d' % gameTime)
        if lastState == 'R':
            self.cButton.setStyleSheet("QRadioButton::indicator:unchecked { background-color: red;}")
        if lastState == 'G':
            self.cButton.setStyleSheet("QRadioButton::indicator:unchecked { background-color: green;}")
        if lastState == 'B':
            self.cButton.setStyleSheet("QRadioButton::indicator:unchecked { background-color: blue;}")
        if lastState == None:
            self.cButton.setStyleSheet("QRadioButton::indicator:checked { background-color: white;}")
        # print('Game Time: %d' %gameTime)
        if(displayState == 'game'):
            self.label.setText('Play clock: %d' %gameTime)
            if not winMQ.empty():
                temp = winMQ.get()
                if temp == 'WIN':
                    finalScore = gameTime
                    for i in reversed(range(self.layout.count())):
                        self.layout.itemAt(i).widget().setParent(None)
                    self.victoryUI()
                    self.show()
                else:
                    # Lose UI
                    # winMQ.queue.clear()
                    while not winMQ.empty():
                        winMQ.get()
                    for i in reversed(range(self.layout.count())):
                        self.layout.itemAt(i).widget().setParent(None)
                    self.loseUI()
                    self.show()

    @pyqtSlot()
    def play_on_click(self):
        print('Play button clicked')
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        global pauseButtonState, gameTime, finalScore, winCondition
        pauseButtonState = True
        winCondition = False
        gameTime = 0
        finalScore = 0
        self.gameUI()
        self.show()

    @pyqtSlot()
    def leader_on_click(self):
        global boardString
        boardString = ''
        print('Leader Board Button Clicked')
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        string = '{"TARGET": "Server", "COMMAND": "get"}'
        s.send(string.encode('utf-8'))
        response = s.recv(size)
        jrep = json.loads(response.decode('utf-8'))
        print(jrep)
        for j in jrep["High Scores"]:
            boardString += '%s - %s\r' % (jrep["High Scores"][j]["Name"], jrep["High Scores"][j]["Score"])
            # TODO: Sort in DESCENDING order of scores
        self.leaderBoardUI()
        self.show()

    @pyqtSlot()
    def submit_on_click(self):
        global gameTime, finalScore, s
        name = self.edit.text()
        payload = '{"TARGET": "Server", "COMMAND": "post", "NAME": "%s", "SCORE": "%s"}' % (name, finalScore)
        s.send(payload.encode('utf-8'))
        print(payload)
        gameTime = 0
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.initUI()
        self.show()

    @pyqtSlot()
    def back_on_click(self):
        global gameTime
        gameTime = 0
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.initUI()
        self.show()

    @pyqtSlot()
    def pause_on_click(self):
        print('Pause button clicked')
        global pauseButtonState
        pauseButtonState = not pauseButtonState
        if(pauseButtonState == False):
            self.timer.stop()
        else:
            self.timer.start()
        for i in reversed(range(self.layout.count())):
            if(not self.layout.itemAt(i).widget() == QTimer):
                self.layout.itemAt(i).widget().setParent(None)
        self.gameUI()
        self.show()

    @pyqtSlot()
    def debug_rgb_click(self):
        os.system('python3 RGB_graph.py &')

    @pyqtSlot()
    def debug_ir_click(self):
        os.system('python3 IR_graph.py &')

    @pyqtSlot()
    def debug_motor_click(self):
        os.system('python3 data_model_encoderOnly.py &')

    @pyqtSlot()
    def w_on_click(self):
        global lastMotorMoveCommand
        lastMotorMoveCommand = "f"
        s.send(b'{"TARGET": "Rover", "COMMAND": "f"}')

    @pyqtSlot()
    def a_on_click(self):
        global lastMotorMoveCommand
        lastMotorMoveCommand = "l"
        s.send(b'{"TARGET": "Rover", "COMMAND": "l"}')

    @pyqtSlot()
    def s_on_click(self):
        global lastMotorMoveCommand
        lastMotorMoveCommand = "b"
        s.send(b'{"TARGET": "Rover", "COMMAND": "b"}')

    @pyqtSlot()
    def d_on_click(self):
        global lastMotorMoveCommand
        lastMotorMoveCommand = "r"
        s.send(b'{"TARGET": "Rover", "COMMAND": "r"}')

    @pyqtSlot()
    def small_r_click(self):
        s.send(b'{"TARGET": "Rover", "COMMAND": "littleR"}')

    @pyqtSlot()
    def small_l_click(self):
        s.send(b'{"TARGET": "Rover", "COMMAND": "littleL"}')

    @pyqtSlot()
    def halt_on_click(self):
        s.send(b'{"TARGET": "Rover", "COMMAND": "s"}')

if __name__ == '__main__':
    try:
        t1 = threading.Thread(target=winReceive)
        t1.start()
        app = QApplication(sys.argv)
        ex = App()
        sys.exit(app.exec())
        print("After exit")
        t1.join()
        print("After thread join")
        s.close()
        s2.close()
    except KeyboardInterrupt:
        t1.join()
        s.close()
        s2.close()
        print(" - Exiting")

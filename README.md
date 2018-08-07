## Pre-Requisites for Running Server
Open up the terminal and execute the following commands:
1) sudo apt-get update

2) sudo apt-get upgrade

3) sudo apt-get install python3 python3-pyqt5

4) pip3 install pymongo

5) pip3 install flask

6) pip3 install flask_socketio

7) pip3 install eventlet

## To kill a process running on a port
* Meaning python won't run, because the TCP/IP port is in use

1) sudo netstat -ap | grep python OR ps aux | grep python
- The only task that should be shown is our python script
- should look something like:
tcp      0    0  0.0.0.0:cisco-sccp     0.0.0.0:*                   LISTEN      900/python3
- the 900 infront of /python3 is the PID of our script

2) kill <PID>

3) If kill <PID> doesn't work, try kill -9 <PID>
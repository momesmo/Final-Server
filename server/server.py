#!/usr/bin/env python3

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from werkzeug.serving import WSGIRequestHandler
import logging
from logging.handlers import RotatingFileHandler
from pymongo import MongoClient
import os

app = Flask(__name__)
api = Api(app)

highscores = {}
count = 0
parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('score')

FILE_NAME = 'server_data.txt'
f = open(FILE_NAME, 'r')
contents = f.read()
contents = contents.split("\n")
for i in contents:
    j = i.split(" ")
    if(len(j[0]) > 0):
        newDict = {
            "Name": j[0],
            "Score": j[1]
            }
        highscores[count] = newDict
        count += 1
f.close()

class AccessHTTP(Resource):
    def get(self): # This route is used to get the High Scores
        # print(returnObj)
        return {"High Scores": highscores}
        # return returnObj
    def post(self): # POST request is used to send user-generated data
        # This route is for adding a new highscore to the Database
        # highscores[name] = score
        args = parser.parse_args()
        global count
        newDict = {
            "Name": args['name'],
            "Score": args['score']
        }
        highscores[count] = newDict
        count += 1

        f = open(FILE_NAME, 'a')
        f.write("%s %s\n" % (args['name'], args['score']))
        f.close()

        return args['name'], 201

        # print(request.data)
    def put(self): # PUT request replaces whatever exists at that URL
        # Implement this later for the motor encoder data
        return {"C": "C"}


api.add_resource(AccessHTTP, '/')

ip = ''
myPort = 4000

if __name__ == '__main__':
    WSGIRequestHandler.protocol_version = 'HTTP/1.1'
    # Logging Stuff
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler('server.log', maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.run(host=ip, port=myPort, debug=True, threaded=True)

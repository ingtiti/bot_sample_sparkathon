#!/usr/bin/env python2
#  -*- coding: utf-8 -*-
#version v1.0
""" Script to demonstrate the use of ciscosparkapi for a bot.

It will query a DB in MongoDB and retrieve a device's details
"""


from __future__ import print_function
from builtins import object
import subprocess
import json
from pymongo import MongoClient
import web
import re
import os
import requests
import datetime
from openpyxl import load_workbook

from ciscosparkapi import CiscoSparkAPI, Webhook


def create_mongodb(config):
    """
        Creates MongoDB Connection and returns the MongoDB client.

    """

    # =====================================================================================
    # This section will be to use the DB -
    # need to start building the connection string
    # =====================================================================================

    mongo_url = "mongodb://"

    mongo_url += ",".join(map(lambda srv: srv['host'] + ":" + str(srv['port']), config['data']['mongoServers']))
    # ==========================================================
    #    If replica sets are available, connect to them as well
    # ==========================================================

    if 'replica' in config['data']:
            mongo_url += "/?replicaSet={0}".format(config['data']['replica'])

            # ==========================================================
            #    Instantiate Mongo Client using URL created
            # ==========================================================

    client = MongoClient(mongo_url)
    return client

class webhook(object):
    def POST(self):
        """Respond to inbound webhook JSON HTTP POSTs from Cisco Spark."""
        # Get the POST data sent from Spark
        json_data = web.data()
        print("\nWEBHOOK POST RECEIVED:")
        print(json_data, "\n")
        #print(type(json_data))
        # Create a Webhook object from the JSON data
        webhook_obj = Webhook(""+json_data)
        # Get the room details
        room = api.rooms.get(webhook_obj.data.roomId)
        # Get the message details
        message = api.messages.get(webhook_obj.data.id)
        # Get the sender's details
        person = api.people.get(message.personId)

        print("NEW MESSAGE IN ROOM '{}'".format(room.title))
        print("FROM '{}'".format(person.displayName))
        #print("MESSAGE '{}'\n".format(message.text))
        #print("MESSAGE CONTENT '{}'\n".format(message.files))
        # This is a VERY IMPORTANT loop prevention control step.
        # If you respond to all messages...  You will respond to the messages
        # that the bot posts and thereby create a loop condition.
        me = api.people.me()
        if message.personId == me.id:
            # Message was sent by me (bot); do not respond.
            return 'OK'
        else:
            # Message was sent by someone else; parse message and respond.
	    #print(list(message))
            
            '''
            
            The CORE of the bot. This will enable the different commands available to the bot.
            '''
            if re.search("check (.*)", message.text):
                id_device = re.search("check (.*)", message.text).group(1)

                
                details_device = list(mongoDatabase.find({'idDevice': id_device}))
                if(len(details_device)>0):
                    api.messages.create(room.id, markdown="Ok "+person.displayName.split(' ')[0]+ ", here's what I got for **"+id_device+"**")
                    
                    for val, item in enumerate(details_device):
                        
                         
                        markdown = ("- Description: **" + item['description']+''
                                    "** \n- Current List Price: **" + str(item['listPrice'])+' galleons**')
                                    
                        
                                                   
                        api.messages.create(room.id,markdown=markdown)
                        
                else:
                    response_message = api.messages.create(room.id, text="Sorry " + person.displayName.split(' ')[0] + ", I couldn't find the device in my database. Please try again")
                        
        
               
            elif "help" in message.text:
                response_message=api.messages.create(room.id, markdown="Hi " + person.displayName.split(' ')[0] + ", I respond to two commands **help** and **check** ")
                response_message=api.messages.create(room.id, markdown=" You can use the second one like the following     '**check ASR-903** and I'll provide the details of said device'")
                response_message=api.messages.create(room.id, markdown="===========================================")
                
            else:
                #unrecognized commands
                response_message = api.messages.create(room.id, markdown="Sorry " + person.displayName.split(' ')[0] + " I couldn't understand the command. Please try again **Available commands = help and check**")

        return 'OK'



# Global variables

# Your Spark webhook should point to http://<serverip>:8080/sparkwebhook
urls = ('/sparkwebhook', 'webhook')
# Create the web application instance
app = web.application(urls, globals())

# Mongo variables
with open('config.json', 'r') as f:
    config = json.load(f)

# Create the Cisco Spark API connection object
api = CiscoSparkAPI(config['token'])

# Connect to the database
mongo_db_cnxn = create_mongodb(config)
db = mongo_db_cnxn[config['data']['database']]
# authenticate
result = db.authenticate(config['data']['username'], config['data']['password'])
mongoDatabase=db.devices

if mongoDatabase:
    print("DB connection is online: True")
if __name__ == '__main__':
    # Start the web.py web server
    app.run()


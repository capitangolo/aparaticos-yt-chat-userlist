#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os


JSON_FILE = './raffle.json'


users = set()
user_counter = 0
names = []

def load(config):
    global users
    global user_counter
    global names

    # Apply config
    if 'ignore_users' in config.keys():
        users.update(config['ignore_users'])

    # Load users from last execution
    if os.path.isfile(JSON_FILE):
        with open(JSON_FILE) as json_file:
            data = json.load(json_file)
            names = data

    for name in names:
        global user_couner
        user_counter += 1
        users.add(name['user'])
        # TODO: Output to a file
        print('{}  {}'.format(name['id'], name['user']))


def process_chatMessage(chatMessage):
    global users
    global user_counter
    global names

    author_name = chatMessage['authorDetails']['displayName']
    if not author_name in users:
        global user_counter
        user_counter += 1

        names.append({"id": user_counter, "user": author_name})
        with open(JSON_FILE, 'w') as outfile:
            json.dump(names, outfile)

        users.add(author_name)

        # TODO: Output to a file
        print('{}  {}'.format(user_counter, author_name))

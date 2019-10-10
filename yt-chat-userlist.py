#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import signal
import sys
import time

from apiclient.errors import HttpError
from oauth2client.tools import argparser
from yt_chat import google_api

## --------------
## TODO: Move this to a 'youtube-api' module.

def list_scheduled_broadcasts(youtube):
    broadcasts = list_broadcasts(youtube)

    scheduled_broadcasts = []

    for broadcast in broadcasts:
        if not 'status' in broadcast.keys():
            continue
        status = broadcast['status']

        if not 'lifeCycleStatus' in status.keys():
            continue
        lifeCycleStatus = status['lifeCycleStatus']

        nonvalid_status = ['complete','revoked']
        if lifeCycleStatus in nonvalid_status:
            continue

        scheduled_broadcasts.append(broadcast)
    return scheduled_broadcasts

def list_broadcasts(youtube):
    broadcasts = []

    list_streams_request = youtube.liveBroadcasts().list(
        part='id,snippet,contentDetails,status',
        mine=True,
        maxResults=50
    )

    while list_streams_request:
        list_streams_response = list_streams_request.execute()

        for stream in list_streams_response.get('items', []):
            broadcasts.append(stream)

        list_streams_request = youtube.liveBroadcasts().list_next(
            list_streams_request, list_streams_response)

    return broadcasts

def list_chatmessages_users(youtube, liveChatId):
    list_streams_request = youtube.liveChatMessages().list(
        liveChatId = liveChatId,
        part="id,snippet,authorDetails"
    )

    while list_streams_request:
        list_streams_response = list_streams_request.execute()

        for chatMessage in list_streams_response.get("items", []):
            aparaticos_process_chatMessage(chatMessage)

        time.sleep(list_streams_response['pollingIntervalMillis'] / 1000.0)

        list_streams_request = youtube.liveChatMessages().list_next(
            list_streams_request, list_streams_response)

def signal_handler(sig, frame):
    sys.exit(0)

##
## --------------


## --------------
## All this is specific to our livestream.
# TODO: Move this to plugins
# TODO: Use output files instead of the console
def aparaticos_process_chatMessage(chatMessage):
    author_name = chatMessage['authorDetails']['displayName']
    if not author_name in users:
        global user_counter
        user_counter += 1
        names.append({"id": user_counter, "user": author_name})
        json_file = './sorteo.json'
        with open(json_file, 'w') as outfile:
            json.dump(names, outfile)
        users.add(author_name)
        print('{}  {}'.format(user_counter, author_name))



users = set()
#users.add(u'Víctor Jiménez Cerrada')
#users.add(u'Aparaticos')
#users.add(u'daniel falcon')

user_counter = 0

names = []

##
## --------------

if __name__ == "__main__":
# This will be used… eventually…
#    argparser.add_argument('-o', '--output-folder', default=os.path.join(os.getcwd(), 'output'),
#        help='Plugins can use this folder to output stuff and save status.')
#    argparser.add_argument('-c', '--config', default=os.path.join(os.getcwd(), 'config.json'),
#        help='Read configuration from this file.')
#    argparser.add_argument('-s', '--session-id', default='default',
#        help='An identifier for the session, output will be tagged with this id.')
    args = argparser.parse_args()
    signal.signal(signal.SIGINT, signal_handler)

## --------------
## All this is specific to our livestream.
# TODO: Move this to plugins
    json_file = './sorteo.json'
    if os.path.isfile(json_file):
        with open(json_file) as json_file:
            data = json.load(json_file)
            names = data

    for name in names:
        global user_couner
        user_counter += 1
        users.add(name['user'])
        print('{}  {}'.format(name['id'], name['user']))

##
## --------------

    print('Fetching your youtube livestreams, wait a bit…\n')
    youtube = google_api.get_authenticated_service(args)

    try:
        broadcasts = list_scheduled_broadcasts(youtube)

        print('\nSelect stream to manage and press enter:\n')
        i = -1
        for broadcast in broadcasts:
            title = broadcast['snippet']['title']
            status = broadcast['status']['lifeCycleStatus']
            id = broadcast['id']
            liveChat = broadcast['snippet']['liveChatId']

            i += 1
            print('{}. {} ({}) - {} {}'.format(i, title, status, id, liveChat))

        index = int(input('\nStream id [0-{}]: '.format(i)))
        broadcast = broadcasts[index]
        if index > i or index < 0:
            print('{} is not a valid id. Numbers between 0 and {}'.format(index, i))
            exit(0)

        print('Managing: {}. {} ({})'.format(index, broadcast['snippet']['title'], broadcast['status']['lifeCycleStatus']))

        id = broadcast['id']
        channelId = broadcast['snippet']['channelId']
        print('Info:')
        print('id: {}'.format(id))
        print('public url: https://youtube.com/watch?v={}'.format(id))
        print('public chat url: https://www.youtube.com/live_chat?v={}'.format(id))
        print('studio url: https://studio.youtube.com/channel/{}/livestreaming/dashboard?v={}'.format(channelId, id))
        print('studio chat url: https://studio.youtube.com/live_chat?v={}'.format(id))
        print('\nChat:')

        liveChat = broadcast['snippet']['liveChatId']
        list_chatmessages_users(youtube, liveChat)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))


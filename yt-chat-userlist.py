#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import signal
import sys

from apiclient.errors import HttpError
from oauth2client.tools import argparser
from yt_chat import google_api, youtube_api
from yt_chat.plugins import raffle


def signal_handler(sig, frame):
    sys.exit(0)


event_listeners = {}

EVENTS = [
    'process_chatMessage'
]

def load_plugin(plugin, config):
    plugin.load(config)

    # register in events
    for event in EVENTS:
        if hasattr(plugin, event):
            event_listener = event_listeners[event]
            event_listener.add(getattr(plugin, event))

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

    # Load plugins
    plugins = [raffle] # TODO: Load from plugin module.
    config = {
        'yt_chat.plugins.raffle': {
            'ignore_users': ['Víctor Jiménez Cerrada', 'Aparaticos', 'daniel falcon']
        }
    }
    for event in EVENTS:
        if event not in event_listeners.keys():
            event_listeners[event] = set()
    for plugin in plugins:
        load_plugin(plugin, config[raffle.__name__])

    # Load Streams
    print('Fetching your youtube livestreams, wait a bit…')
    youtube = google_api.get_authenticated_service(args)

    try:
        broadcasts = youtube_api.list_scheduled_broadcasts(youtube, event_listeners)

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
        youtube_api.list_chatmessages_users(youtube, liveChat, event_listeners)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))


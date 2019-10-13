#!/usr/bin/python
# -*- coding: utf-8 -*-


import time


def list_scheduled_broadcasts(youtube, event_listeners):
    broadcasts = list_broadcasts(youtube, event_listeners)

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


def list_broadcasts(youtube, event_listeners):
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


def list_chatmessages_users(youtube, liveChatId, event_listeners):
    list_streams_request = youtube.liveChatMessages().list(
        liveChatId = liveChatId,
        part="id,snippet,authorDetails"
    )

    processors = event_listeners['process_chatMessage']

    while list_streams_request:
        list_streams_response = list_streams_request.execute()

        for chatMessage in list_streams_response.get("items", []):
            for processor in processors:
                processor(chatMessage)

        time.sleep(list_streams_response['pollingIntervalMillis'] / 1000.0)

        list_streams_request = youtube.liveChatMessages().list_next(
            list_streams_request, list_streams_response)


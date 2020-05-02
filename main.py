#!/usr/bin/env python3
# coding=utf8

"""
Logging bot for Slack.

Writes to disk all events in subscribed channels.
All events from single channel are written to one file.
Every event written in file as a separate JSON object.
Events are separated by newline char.
"""

import argparse
import json
import logging
import os
import os.path
import sys
import time

import slack


# List of RTM events to intercept.
# See https://api.slack.com/events
EVENT_TYPES = [
    'file_change',
    'file_comment_added',
    'file_comment_deleted',
    'file_comment_edited',
    'file_created',
    'file_deleted',
    'file_public',
    'file_shared',
    'file_unshared',
    'member_joined_channel',
    'member_left_channel',
    'message',
    'pin_added',
    'pin_removed',
    'reaction_added',
    'reaction_removed'
]


class Nestor:
    """
    Incapsulates essential bot data.
    """

    def __init__(self, token, dst, verbose, react):
        """
        Constructor.

        :param token: Bot OAuth token
        :type token: string

        :param dst: path to a destination directory
        :type dst: string

        :param verbose: use increased logging or not
        :type verbose: boolean

        :param react: react on every saved message with emoji or not
        :type react: boolean
        """
        os.makedirs(dst, exist_ok=True)
        self.__dst = dst
        self.__token = token
        self.__react = react
        logging.basicConfig(
            format='%(asctime)s %(name)s %(levelname)8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.DEBUG if verbose else logging.INFO)
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__users = {}  # user names cache

    def __on_event(self, event_type, data, web_client):
        """
        Unified handler for every event type intercepted.

        :param event_type: event type identifier. Valid types
            listed in https://api.slack.com/events
        :type event_type: string

        :param data: dictionary with event payload. As far as it
            differs from event type to event type, no detailed
            description can be given.
        :type data: dict

        :param web_client:
        :type web_client: instance of slack.WebClient
        """
        data['event_type_'] = event_type
        # extend
        channel_id = _get_channel_id(data)
        if not channel_id:
            self.__logger.warning('no channel id: %r', data)
            return
        self.__augment(data, web_client)
        self.__logger.debug('event: %r', data)
        # save
        fname = os.path.join(self.__dst, channel_id)
        with open(fname, 'a') as fdescr:
            json.dump(data, fdescr, separators=(',', ':'), sort_keys=True)
            fdescr.write('\n')
        # react
        if (event_type == 'message' and 'subtype' not in data and self.__react):
            web_client.reactions_add(name='floppy_disk', channel=channel_id,
                                     timestamp=data['ts'])

    def __augment(self, data, web_client):
        """
        Enrich event payload with some data, if applicable.

        :param data: event payload
        :type data: dict

        :param web_client: Slack API handle
        :type web_client: instance of slack.WebClient
        """
        # extend event with human readable UTC date&time
        tstmp = data.get('ts')
        if tstmp:
            tstmp = float(tstmp)
            data['ts_'] = time.strftime('%Y-%m-%d %T', time.gmtime(tstmp))
        # resolve user name from user ID
        user_id = _get_user_id(data)
        if user_id:
            name = self.__users.get(user_id)
            if not name:
                info = web_client.users_info(user=user_id)
                name = info['user']['name']
                self.__users[user_id] = name
            data['user_'] = name

    def start(self):
        """
        Start the bot. No return.
        """
        for event in EVENT_TYPES:
            def wrapper(etype):
                def fun(**kwargs):
                    try:
                        data = kwargs['data']
                        web_client = kwargs['web_client']
                        self.__on_event(etype, data, web_client)
                    except Exception:
                        self.__logger.error('event handler crashed.'
                                            ' event_type: %r; data: %r',
                                            etype, kwargs, exc_info=True)
                return fun
            slack.RTMClient.on(event=event, callback=wrapper(event))
        self.__logger.info('starting')
        slack.RTMClient(token=self.__token).start()


def _get_channel_id(data):
    """
    Get channel ID which this event data is associated to.
    Event payload schema highly depends on event type.

    :param data: event payload
    :type data: dict

    :rtype: non empty string or None
    """
    for key in ['channel', 'channel_id']:
        channel = data.get(key)
        if channel:
            return channel
    channel = data.get('item', {}).get('channel')
    if channel:
        return channel
    return None


def _get_user_id(data):
    """
    Get user ID which this event is generated by.
    Event payload schema highly depends on event type.

    :param data: event payload
    :type data: dict

    :rtype: non empty string or None
    """
    for key in ['user', 'user_id']:
        user = data.get(key)
        if user:
            return user
    return None


if __name__ == "__main__":
    try:
        PARSER = argparse.ArgumentParser(description=__doc__)
        PARSER.add_argument('-v', '--verbose', action='store_true',
                            help='Be verbose')
        PARSER.add_argument('-r', '--react', action='store_true',
                            help='React on every successful saved message')
        PARSER.add_argument('destination',
                            help='Destination directory to write events to')
        ARGS = PARSER.parse_args()
        TOKEN = os.environ['TOKEN']
        Nestor(TOKEN, ARGS.destination, ARGS.verbose, ARGS.react).start()
    except KeyboardInterrupt:
        print('interrupted by user')
        sys.exit(1)

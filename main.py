#!/usr/bin/env python3
# coding=utf8

import argparse
import json
import logging
import os
import sys

import slack


# Default values
DEF_LOGLEVEL = 'warning'

LOGGER = None
BOT_ID = None


def update_bot_id(web_client, **kwargs):
    global BOT_ID
    if not BOT_ID:
        BOT_ID = web_client.auth_test()["user_id"]
        LOGGER.info("bot ID: %r", BOT_ID)


def on_event(event_type, data, web_client, **kwargs):
    LOGGER.debug('event_type: %r; data: %r', event_type, data)


def main():
    # parse command line
    parser = argparse.ArgumentParser(
        description='Archiving bot for Slack')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Be verbose')
    args = parser.parse_args()

    # configure logging
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG if args.verbose else logging.INFO)
    global LOGGER
    LOGGER = logging.getLogger('nestor')
    LOGGER.info('started')

    # register callbacks
    events = [
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
    for event in events:
        def wrapper(e):
            def f(**kwargs):
                on_event(event_type=e, **kwargs)
            return f
        slack.RTMClient.on(event=event, callback=wrapper(event))

    # instantiate API client
    slack.RTMClient(token=os.environ.get('TOKEN')).start()


if __name__ == "__main__":
    try:
        main()
        LOGGER.info('terminated')
    except KeyboardInterrupt:
        if LOGGER:
            LOGGER.info('interrupted by user')
        sys.exit(1)
    except Exception as exc:
        if LOGGER:
            LOGGER.critical('crashed: %s', exc, exc_info=True)
            sys.exit(1)
        raise

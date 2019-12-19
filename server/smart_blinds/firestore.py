import datetime
import logging
import os

import firebase_admin
from firebase_admin import credentials, firestore

from .config import config


class Collections():
    CHANNELS = 'channels'
    COMMANDS = 'commands'

    def __init__(self):
        pass


class ChannelFields():
    NAME = 'name'
    LABEL = 'label'
    STATUS = 'status'

    CHANNEL = 'channel'
    LAST_ACTION = 'last_action'
    AVAILBLE_ACTIONS = 'available_actions'
    USER = 'user'
    TIMESTAMP = 'timestamp'

    def __init__(self):
        pass


class CommandFields():
    CHANNEL = 'channel'
    ACTION = 'action'
    TIMESTAMP = 'timestamp'

    def __init__(self):
        pass


class Actions():
    IDLE = 'idle'
    OPEN = 'open'
    CLOSE = 'close'
    STOP = 'stop'
    OPEN_30_PERCENT = 'open_30_percent'
    POSITION_TOGGLE = 'position_toggle'

    def __init__(self):
        pass


class ChannelStatus():
    IDLE = 'idle'
    WORKING = 'working'

    def __init__(self):
        pass


cred_path = os.path.join('../', config['serviceAccountFileName'])
cred = credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred)

def get_db_client():
    return firestore.client()

def init_db(channels):
    logging.info('[init_db] Start db initialization')

    db = get_db_client()

    for key, channel in channels.items():
        logging.info('Initialising channel in firestore: {0}'.format(key))

        label = channel[ChannelFields.LABEL]

        doc_ref = db.collection(Collections.CHANNELS).document(key)

        doc_ref.set({
            ChannelFields.NAME: key,
            ChannelFields.LABEL: label,
            ChannelFields.STATUS: Actions.IDLE,
            ChannelFields.LAST_ACTION: '',
            ChannelFields.AVAILBLE_ACTIONS: [Actions.OPEN, Actions.OPEN_30_PERCENT, Actions.POSITION_TOGGLE, Actions.CLOSE, Actions.STOP],
        }, merge=True)
    logging.info('[init_db] End db initialization')

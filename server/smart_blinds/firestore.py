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


ACCEPTED_CHANGE_TYPE_NAME = 'ADDED'


class Firestore():
    def __init__(self, command_callback):
        logging.info('[Firestore] Start initialising firestore connection')
        self.doc_watch = None
        self.command_callback = command_callback

        cred_path = os.path.join('../', config['serviceAccountFileName'])
        cred = credentials.Certificate(cred_path)

        firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        logging.info('[Firestore] End initialising firestore connection')

    def init_db(self, channels):
        logging.info('[Firestore] Start db initialization')

        for key, channel in channels.items():
            logging.info('Initialising channel in firestore: {0}'.format(key))

            label = channel[ChannelFields.LABEL]

            doc_ref = self.db.collection(Collections.CHANNELS).document(key)

            doc_ref.set({
                ChannelFields.NAME: key,
                ChannelFields.LABEL: label,
                ChannelFields.STATUS: Actions.IDLE,
                ChannelFields.LAST_ACTION: '',
                ChannelFields.AVAILBLE_ACTIONS: [Actions.OPEN, Actions.OPEN_30_PERCENT, Actions.POSITION_TOGGLE, Actions.CLOSE, Actions.STOP],
            }, merge=True)
        logging.info('[Firestore] End db initialization')

    def on_snapshot(self, docs, changes, read_time):
        for change in changes:
            if change.type.name == ACCEPTED_CHANGE_TYPE_NAME and self.command_callback != None:
                self.command_callback(change.document.get(
                    CommandFields.ACTION), change.document.get(CommandFields.CHANNEL))

    def start(self):
        logging.info('[Firestore] Start watchign db changes')
        colection_ref = self.db.collection(Collections.COMMANDS)
        query_ref = colection_ref.order_by(
            CommandFields.TIMESTAMP, direction=firestore.Query.DESCENDING).limit(1)
        self.doc_watch = query_ref.on_snapshot(self.on_snapshot)

    def stop(self):
        if self.doc_watch != None:
            logging.info('[Firestore] End watchign db changes')
            self.doc_watch.unsubscribe()
            self.doc_watch = None

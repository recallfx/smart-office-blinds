import datetime
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
SERVICE_ACCOUNT_KEY_FILE_NAME = 'service_account_key.json'


class Firestore():

    def __init__(self, channels, command_callback):
        self.doc_watch = None
        self.command_callback = command_callback

        cred_path = os.path.join('../', config['serviceAccountFileName'])
        cred = credentials.Certificate(cred_path)

        firebase_admin.initialize_app(cred)

        self.db = firestore.client()

        self.init_db(channels)

    def init_db(self, channels):
        print('[INFO] Initialising channels')

        for key, channel in channels.items():
            print('[INFO] Initialising channel in firestore: {0}'.format(key))

            label = channel[ChannelFields.LABEL]

            doc_ref = self.db.collection(Collections.CHANNELS).document(key)

            doc_ref.set({
                ChannelFields.NAME: key,
                ChannelFields.LABEL: label,
                ChannelFields.STATUS: Actions.IDLE,
                ChannelFields.LAST_ACTION: '',
                ChannelFields.AVAILBLE_ACTIONS: [Actions.OPEN, Actions.OPEN_30_PERCENT, Actions.POSITION_TOGGLE, Actions.CLOSE],
            }, merge=True)

    def on_snapshot(self, docs, changes, read_time):
        for change in changes:
            if change.type.name == ACCEPTED_CHANGE_TYPE_NAME and self.command_callback != None:
                self.command_callback(change.document.get(
                    CommandFields.ACTION), change.document.get(CommandFields.CHANNEL))

    def start(self):
        colection_ref = self.db.collection(Collections.COMMANDS)
        query_ref = colection_ref.order_by(
            CommandFields.TIMESTAMP, direction=firestore.Query.DESCENDING).limit(1)
        self.doc_watch = query_ref.on_snapshot(self.on_snapshot)

    def stop(self):
        if self.doc_watch != None:
            self.doc_watch.unsubscribe()
            self.doc_watch = None

import os
import datetime
import instance.config as config
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from smart_blinds.smart_blinds import SmartBlinds


class Collections():
    CHANNELS = 'channels'
    COMMANDS = 'commands'

    def __init__(self):
        pass


class Fields():
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


def init_firestore(db, channels):
    for key, channel in channels.items():
        print('Initialising channel in firestore: {0}'.format(key))

        label = channel[Fields.LABEL]

        doc_ref = db.collection(Collections.CHANNELS).document(key)

        try:
            doc_ref.set({
                Fields.NAME: key,
                Fields.LABEL: label,
                Fields.STATUS: Actions.IDLE,
                Fields.LAST_ACTION: '',
                Fields.AVAILBLE_ACTIONS: [Actions.OPEN, Actions.OPEN_30_PERCENT, Actions.POSITION_TOGGLE, Actions.CLOSE],
            }, merge=True)
        except Exception as inst:
            print(u'Something went wrong: ', inst)

def on_command_snapshot(docs, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            run_command(change.document)

def run_command(document):
    smart_blinds.command(document.get('action'), document.get('channel'))

# Set up
DEBUG = True
smart_blinds = SmartBlinds(config.CHANNELS, DEBUG)

# Use a service account
script_dir = os.path.dirname(__file__)
cred_path = os.path.join(
    script_dir, 'instance/sob-mbieliau-firebase-2d798-firebase-adminsdk-4vloy-1b8909b6d9.json')
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

init_firestore(db, config.CHANNELS)


colection_ref = db.collection(Collections.COMMANDS)
query_ref = colection_ref.order_by(
    Fields.TIMESTAMP, direction=firestore.Query.DESCENDING).limit(1)
doc_watch = query_ref.on_snapshot(on_command_snapshot)

while (1):
    pass

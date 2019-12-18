import datetime
import logging
import os
from multiprocessing import Process

import firebase_admin
from firebase_admin import credentials, firestore

from .config import config
from .firestore import Collections


class FirestoreState(Process):
    def __init__(self, queue, **kwargs):
        super(FirestoreState, self).__init__()

        self.queue = queue
        self.started = False

    def run(self):
        logging.info('[FirestoreState] Start initialising firestore connection')
        cred_path = os.path.join('../', config['serviceAccountFileName'])
        cred = credentials.Certificate(cred_path)

        firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        logging.info('[FirestoreState] End initialising firestore connection')
        logging.info('[FirestoreState] Start waiting for state queue')

        try:
            while True:
                data = self.queue.get()

                self.update_db_channel_status(
                    data['channel_name'], data['action'], data['status'])

        except KeyboardInterrupt:
            pass

    def update_db_channel_status(self, channel_name, action, status):
        params = {'status': status}

        if action != None:
            params['last_action'] = action

        logging.info('[FirestoreState] Updating firestore channel: {}, action: {}, status: {}'.format(
            channel_name, action, status))

        try:
            self.db.collection(Collections.CHANNELS).document(
                channel_name).set(params, merge=True)
        except Exception as ex:
            logging.exception(str(ex))

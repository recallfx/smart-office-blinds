import datetime
import logging
import os
import time
from multiprocessing import Process

from firebase_admin import credentials, firestore

from .config import config
from .firestore import Collections, get_db_client


class FirestoreState(Process):
    def __init__(self, queue, **kwargs):
        super(FirestoreState, self).__init__()

        self.queue = queue

    def run(self):
        logging.info(
            '[FirestoreState] Start initialising firestore connection')

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

        logging.debug('[FirestoreState] Updating firestore channel: {}, action: {}, status: {}'.format(
            channel_name, action, status))

        while True:
            try:
                logging.debug('[FirestoreState] Getting db client')
                db = get_db_client()
                logging.debug('[FirestoreState] Got db client, setting data')
                db.collection(Collections.CHANNELS).document(
                    channel_name).set(params, merge=True)
                logging.debug('[FirestoreState] Data set')
            except Exception as ex:
                logging.exception(str(ex))
                time.sleep(0.5)
                continue
            break

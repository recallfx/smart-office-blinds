import logging
import os
from datetime import datetime

from firebase_admin import credentials, firestore

from .config import config
from .firestore import (Actions, ChannelFields, Collections, CommandFields,
                        get_db_client)

ACCEPTED_CHANGE_TYPE_NAME = 'ADDED'
MAX_ACTIVE_INTERVAL_SECONDS = 18000


class FirestoreWatch():
    def __init__(self, command_callback):
        self.doc_watch = None
        self.command_callback = command_callback

    def on_snapshot(self, docs, changes, read_time):
        for change in changes:
            if change.type.name == ACCEPTED_CHANGE_TYPE_NAME:
                self.command_callback(change.document.get(
                    CommandFields.ACTION), change.document.get(CommandFields.CHANNEL))

    def is_active(self):
        date_now = datetime.now()
        elapsed_seconds = (date_now - self.last_check).seconds

        if (elapsed_seconds > MAX_ACTIVE_INTERVAL_SECONDS):
            self.stop()
            return False

        return self.doc_watch != None and self.doc_watch.is_active

    def start(self):
        logging.info('[FirestoreWatch] Start watchign db changes')

        try:
            db = get_db_client()
            colection_ref = db.collection(Collections.COMMANDS)
            query_ref = colection_ref.order_by(
                CommandFields.TIMESTAMP, direction=firestore.Query.DESCENDING).limit(1)
            self.doc_watch = query_ref.on_snapshot(self.on_snapshot)
            self.last_check = datetime.now()

        except KeyboardInterrupt:
            pass
        except Exception as ex:
            logging.exception(
                '[FirestoreWatch] Exception while watching {}'. format(str(ex)))
            self.stop()

    def stop(self):
        try:
            if self.doc_watch != None:
                logging.info('[FirestoreWatch] End watchign db changes')
                self.doc_watch.unsubscribe()
                self.doc_watch = None
        except:
            pass

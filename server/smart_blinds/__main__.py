import argparse
import logging
import time
from multiprocessing import Queue

from .actions import Actions
from .config import config
from .firestore import get_db_client, init_db
from .firestore_state import FirestoreState
from .firestore_watch import FirestoreWatch
from .smart_blinds import SmartBlinds
from .utils import validate_command

CHECK_ACTIVE_TIMER_INTERVAL = 1.0


def server(firestore_watch):
    firestore_watch.start()

    while True:
        try:
            logging.debug('Checking firebase watch')
            if not firestore_watch.is_active():
                logging.info('Restarting firebase watch')
                firestore_watch.start()

            time.sleep(CHECK_ACTIVE_TIMER_INTERVAL)

        except Exception as ex:
            logging.exception(ex)


def main():

    parser = argparse.ArgumentParser(prog='Smart Office Blinds server',
                                     description='Server instance that is dependent on firebase vonnection')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 2.0')
    parser.add_argument('-s', '--server', action='store_true',
                        help='Run as a service. All other arguments are ignored.')
    parser.add_argument('-a', '--action', nargs='?', choices=[
                        Actions.OPEN_30_PERCENT, Actions.POSITION_TOGGLE, Actions.OPEN, Actions.CLOSE, Actions.STOP],
                        default=Actions.STOP)
    parser.add_argument('-c', '--channel', dest='channel', default=None,
                        help='Channel is a servo name assigned to specific remote buttons')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-i', '--init', action='store_true',
                        help='Initialise database schema')

    args = parser.parse_args()

    if (args.debug):
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level)

    state_queue = Queue()
    firestore_watch = None
    firestore_state = None
    smart_blinds = SmartBlinds(
        config['channels'], state_queue, config['debug'])

    try:
        firestore_state = FirestoreState(state_queue)
        firestore_state.start()

        firestore_watch = FirestoreWatch(
            lambda action, channel: smart_blinds.command(action, channel))

        if (args.init):
            init_db(config['channels'])

        if (args.server):
            server(firestore_watch)
        else:
            message = validate_command(
                config['channels'], args.action, args.channel)
            smart_blinds.command(args.action, args.channel)
            logging.info(message)
            time.sleep(5.0)

    except KeyboardInterrupt:
        pass
    except Exception as ex:
        logging.exception(str(ex))
    finally:
        logging.info('Exiting')

        if firestore_watch != None:
            firestore_watch.stop()


if __name__ == "__main__":
    main()

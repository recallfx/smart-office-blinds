import argparse

from .actions import Actions
from .config import config
from .firestore import Firestore
from .smart_blinds import SmartBlinds
from .utils import validate_command


def main():
    parser = argparse.ArgumentParser(prog='Smart Office Blinds server',
                                     description='Server instance that is dependent on firebase vonnection')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 2.0')
    parser.add_argument('-s', '--server', action='store_true',
                        help='Run as a service. All other arguments are ignored.')
    parser.add_argument('-action', nargs='?', choices=[
                        Actions.OPEN_30_PERCENT, Actions.POSITION_TOGGLE, Actions.OPEN, Actions.CLOSE, Actions.STOP],
                        default=Actions.STOP)
    parser.add_argument('-c', '--channel', dest='channel', default=None,
                        help='Channel is a servo name assigned to specific remote buttons')

    args = parser.parse_args()

    firestore = None
    smart_blinds = SmartBlinds(config['channels'], config['debug'])

    try:
        if (args.server):
            firestore = Firestore(config['channels'], lambda action,
                                  channel: smart_blinds.command(action, channel))

            firestore.start()
        else:
            message = validate_command(
                config['channels'], args.action, args.channel)
            smart_blinds.command(args.action, args.channel)
            print('[INFO] {}'.format(message))

        smart_blinds.join_processors()
    except KeyboardInterrupt:
        print('[INFO] Exiting')

        if firestore != None:
            firestore.stop()


if __name__ == "__main__":
    main()

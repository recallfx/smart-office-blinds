import argparse

import instance.config as config
from .actions import Actions
from .smart_blinds import SmartBlinds


def main():
    parser = argparse.ArgumentParser(description='Smart office blinds')
    parser.add_argument('action', choices=[
        Actions.IDLE, Actions.OPEN, Actions.CLOSE, Actions.STOP])

    parser.add_argument('-c', '--channel', dest='channel',
                        default=None, help='Channel is a servo name assigned to specific remote buttons (default: auto)')
    parser.add_argument('-u', '--user-name', dest='user',
                        default=None, help='User name if channel is auto (default: none)')

    args = parser.parse_args()

    smart_blinds = SmartBlinds(
        {'CHANNELS': config.CHANNELS, 'DATA': config.DATA, 'DEBUG': config.DEBUG})
    smart_blinds.command(args.action, args.channel, args.user)

    try:
        smart_blinds.join_processors()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

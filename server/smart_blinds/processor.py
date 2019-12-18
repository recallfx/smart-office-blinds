# -*- coding: utf-8 -*-

import requests
from multiprocessing import Process, Queue

from .actions import Actions
from .channel_statuses import ChannelStatuses
from .blinds_api import BlindsApi

from .config import config

class Processor(Process):
    def __init__(self, channel, channel_name, debug_mode, **kwargs):
        super(Processor, self).__init__()
        self.queue = Queue(1)
        self.kwargs = kwargs
        self.blinds = BlindsApi(channel, debug_mode)
        self.channel_name = channel_name
        self.debug_mode = debug_mode

    def run(self):
        try:
            while True:
                command = self.queue.get()

                if command == Actions.OPEN_30_PERCENT:
                    if self.blinds.can_open_partly():
                        self.update_channel_status(
                            ChannelStatuses.BUSY, command)
                        self.blinds.open_30_percent()
                        self.update_channel_status(ChannelStatuses.IDLE)
                if command == Actions.POSITION_TOGGLE:
                    if self.blinds.can_toggle_position():
                        self.update_channel_status(
                            ChannelStatuses.BUSY, command)
                        self.blinds.position_toggle()
                        self.update_channel_status(ChannelStatuses.IDLE)
                if command == Actions.OPEN:
                    if self.blinds.can_open():
                        self.update_channel_status(
                            ChannelStatuses.BUSY, command)
                        self.blinds.open()
                        self.update_channel_status(ChannelStatuses.IDLE)
                if command == Actions.CLOSE:
                    if self.blinds.can_close():
                        self.update_channel_status(
                            ChannelStatuses.BUSY, command)
                        self.blinds.close()
                        self.update_channel_status(ChannelStatuses.IDLE)
                if command == Actions.STOP:
                    if self.blinds.can_stop():
                        self.update_channel_status(
                            ChannelStatuses.BUSY, command)
                        self.blinds.stop()
                        self.update_channel_status(ChannelStatuses.IDLE)
        except KeyboardInterrupt:
            pass

    def update_channel_status(self, status, action=None):
        data = {'channel': self.channel_name, 'status': status, 'auth_token': config['availableApiTokens'][0]}

        if (action is not None):
            data['action'] = action

        response = requests.get(config['cloudFunctionsUrl'] +
                                'setChannelStatus', params=data)

        print('[INFO] Update channel {} action "{}" status "{}"'.format(
            self.channel_name, action, status))

        if self.debug_mode:
            print('[DEBUG] Response: {}'.format(response.text))

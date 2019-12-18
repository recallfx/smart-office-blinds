# -*- coding: utf-8 -*-

import logging
from multiprocessing import Process, Queue

import requests

from .actions import Actions
from .blinds_api import BlindsApi
from .channel_statuses import ChannelStatuses
from .config import config


class Processor(Process):
    def __init__(self, channel, channel_name, status_queue, debug_mode, **kwargs):
        super(Processor, self).__init__()
        self.queue = Queue()
        self.status_queue = status_queue
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
                        self.broadcast_status(ChannelStatuses.BUSY, command)
                        self.blinds.open_30_percent()
                        self.broadcast_status(ChannelStatuses.IDLE)
                if command == Actions.POSITION_TOGGLE:
                    if self.blinds.can_toggle_position():
                        self.broadcast_status(ChannelStatuses.BUSY, command)
                        self.blinds.position_toggle()
                        self.broadcast_status(ChannelStatuses.IDLE)
                if command == Actions.OPEN:
                    if self.blinds.can_open():
                        self.broadcast_status(ChannelStatuses.BUSY, command)
                        self.blinds.open()
                        self.broadcast_status(ChannelStatuses.IDLE)
                if command == Actions.CLOSE:
                    if self.blinds.can_close():
                        self.broadcast_status(ChannelStatuses.BUSY, command)
                        self.blinds.close()
                        self.broadcast_status(ChannelStatuses.IDLE)
                if command == Actions.STOP:
                    if self.blinds.can_stop():
                        self.broadcast_status(ChannelStatuses.BUSY, command)
                        self.blinds.stop()
                        self.broadcast_status(ChannelStatuses.IDLE)
        except KeyboardInterrupt:
            pass

    def broadcast_status(self, status, action=None):
        data = {'channel_name': self.channel_name, 'status': status, 'action': action}

        self.status_queue.put(data)

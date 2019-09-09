# -*- coding: utf-8 -*-

from .actions import Actions
from .processor import Processor

class SmartBlinds():
    def __init__(self, channels, debug_mode=False):
        if channels is None:
            raise AssertionError('Missing channels')

        self.processors = {}

        for key, channel in channels.items():
            print('Initialising channel processor: {0}'.format(key))
            self.processors[key] = Processor(channel, debug_mode)
            self.processors[key].start()

    def command(self, action, channel_name=None):
        if action == Actions.OPEN:
            self.processors[channel_name].queue.put('open')

        if action == Actions.CLOSE:
            self.processors[channel_name].queue.put('close')

        if action == Actions.STOP:
            self.processors[channel_name].queue.put('stop')

    def join_processors(self):
        for _, processor in self.processors.items():
            processor.join()

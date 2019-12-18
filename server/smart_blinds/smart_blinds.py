# -*- coding: utf-8 -*-

from .processor import Processor


class SmartBlinds():
    def __init__(self, channels, debug_mode=False):
        if channels is None:
            raise AssertionError('Missing channels')

        self.processors = {}

        for key, channel in channels.items():
            print('[INFO] Initialising channel processor: {0}'.format(key))
            self.processors[key] = Processor(channel, key, debug_mode)
            self.processors[key].start()

    def command(self, action, channel_name=None):
        print('[INFO] Received command action: {}, channel name: {action}'.format(channel_name))
        self.processors[channel_name].queue.put(action)

    def join_processors(self):
        for _, processor in self.processors.items():
            processor.join()

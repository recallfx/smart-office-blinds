# -*- coding: utf-8 -*-

import logging

from .processor import Processor


class SmartBlinds():
    def __init__(self, channels, debug_mode=False):
        if channels is None:
            raise AssertionError('Missing channels')

        self.processors = {}

        for key, channel in channels.items():
            logging.info('Initialising channel processor: {0}'.format(key))
            self.processors[key] = Processor(channel, key, debug_mode)
            self.processors[key].start()

    def command(self, action, channel_name=None):
        logging.info('Received command action: {}, channel name: {}'.format(
            action, channel_name))
        self.processors[channel_name].queue.put(action)

    def join_processors(self):
        for _, processor in self.processors.items():
            processor.join()

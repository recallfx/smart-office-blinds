# -*- coding: utf-8 -*-

from multiprocessing import Process, Queue

from .actions import Actions
from .blinds_api import BlindsApi


class Processor(Process):
    def __init__(self, channel, debug_mode, **kwargs):
        super(Processor, self).__init__()
        self.queue = Queue(1)
        self.kwargs = kwargs
        self.blinds = BlindsApi(channel, debug_mode)

    def run(self):
        try:
            while True:
                command = self.queue.get()

                if command == Actions.OPEN:
                    self.blinds.open()
                if command == Actions.CLOSE:
                    self.blinds.close()
                if command == Actions.STOP:
                    self.blinds.stop()
        except KeyboardInterrupt:
            pass

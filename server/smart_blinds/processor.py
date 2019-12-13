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

                if command == Actions.OPEN_30_PERCENT:
                    if self.blinds.can_open_partly():
                        self.blinds.open_30_percent()
                if command == Actions.POSITION_TOGGLE:
                    if self.blinds.can_toggle_position():
                        self.blinds.position_toggle()
                if command == Actions.OPEN:
                    if self.blinds.can_open():
                        self.blinds.open()
                if command == Actions.CLOSE:
                    if self.blinds.can_close():
                        self.update_channel_status('busy', command)
                        self.blinds.close()
                        self.update_channel_status('idle')
                if command == Actions.STOP:
                    if self.blinds.can_stop():
                        self.blinds.stop()
        except KeyboardInterrupt:
            pass

    def update_channel_status(status, action = None):
        data = {'channel': self.blinds.channel, 'status': status}

        if (action is not None):
            data.update({'action': action})

        response = requests.get('https://us-central1-sob-mbieliau-firebase-2d798.cloudfunctions.net/setChannelStatus', params=data)

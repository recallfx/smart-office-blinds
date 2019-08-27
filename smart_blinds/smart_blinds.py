# -*- coding: utf-8 -*-

import json

from .actions import Actions
from .processor import Processor


def _get_processors(channels, debug_mode=False):
    processors = {}

    for key, channel in channels.items():
        print('Initialising channel processor: {0}'.format(key))
        processors[key] = Processor(channel, debug_mode)
        processors[key].start()

    return processors


def _get_room_id_map(file_name):
    room_ids = {}

    print('Loading data from file: ' + file_name)

    with open(file_name) as json_file:
        map_data = json.load(json_file)
        seats = map_data['data']['floors'][0]['seats']

        print('Building room id map')

        for seat in seats:
            if not seat is None:
                if "employee" in seat and not seat["employee"] is None:
                    emplyee = seat["employee"]

                    if "fullName" in emplyee and not emplyee["fullName"] is None:
                        full_name = emplyee["fullName"].replace(
                            " ", ".").lower()

                        if "room" in seat and not seat["room"] is None:
                            room = seat["room"]

                            if "id" in seat and not room["id"] is None:
                                room_ids[full_name] = room["id"]

    return room_ids


class SmartBlinds():
    def __init__(self, config):
        if config is None:
            raise ValueError('Missing config')

        self.config = config
        self.channels = self.config["CHANNELS"]
        self.debug_mode = self.config["DEBUG"]

        self.processors = _get_processors(self.channels, self.debug_mode)

        self.room_id_map = _get_room_id_map(self.config["DATA"])

        if self.debug_mode:
            print('Finished initalisation. Room id map size: ' +
                  str(len(self.room_id_map.keys())))

    def _find_room_id(self, user_name):
        if user_name in self.room_id_map and self.room_id_map[user_name]:
            return self.room_id_map[user_name]

        return None

    def _find_channel(self, room_id):
        for key, channel in self.channels.items():
            room_interval = channel['room_interval']
            if not room_interval is None:
                if room_interval[0] <= int(room_id) <= room_interval[1]:
                    return key
        return None

    def command(self, action, channel_name=None, user_name=None):
        if channel_name is None:
            if user_name is None:
                raise AssertionError(
                    'User name must be provided when channel is auto.')

            room_id = self._find_room_id(user_name)

            if room_id is None:
                raise LookupError('Could not find your seat!')

            channel_name = self._find_channel(room_id)

            if channel_name is None:
                raise LookupError('Could not find your channel, try manually.')

        print(channel_name)
        if not channel_name in self.processors.keys():
            raise AssertionError('Unsupported channel "{0}"'.format(channel_name))

        if action == Actions.OPEN:
            self.processors[channel_name].queue.put('open')
            return 'Opening blinds... ' + channel_name

        if action == Actions.CLOSE:
            self.processors[channel_name].queue.put('close')
            return 'Closing blinds... ' + channel_name

        if action == Actions.STOP:
            self.processors[channel_name].queue.put('stop')
            return 'Stopping current operation...  ' + channel_name

        raise AssertionError('Unsupported action "{0}"'.format(action))

    def join_processors(self):
        for _, processor in self.processors.items():
            processor.join()

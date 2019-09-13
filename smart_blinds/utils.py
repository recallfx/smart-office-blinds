import inspect
import json
import unicodedata

from .actions import Actions

def logger_message(user_name, message):
    method_name = inspect.stack()[1][3]

    return '[{0}:{1}] {2}'.format(method_name, user_name, str(message))


def get_room_id_map(file_name):
    room_ids = {}

    with open(file_name) as json_file:
        map_data = json.load(json_file)
        seats = map_data['data']['floors'][0]['seats']

        for seat in seats:
            if not seat is None:
                if "employee" in seat and not seat["employee"] is None:
                    emplyee = seat["employee"]

                    if "fullName" in emplyee and not emplyee["fullName"] is None:
                        full_name = emplyee["fullName"]
                        full_name = unicodedata.normalize('NFKD', full_name).encode(
                            'ascii', 'ignore').decode("utf-8")
                        user_name = full_name.replace(" ", ".").lower()

                        if "room" in seat and not seat["room"] is None:
                            room = seat["room"]

                            if "id" in seat and not room["id"] is None:
                                room_ids[user_name] = room["id"]

    return room_ids


def get_user_name(email):
    email_split = email.split('@')

    if len(email_split) > 1:
        return email_split[0]

    return email


def _find_room_id(room_id_map, user_name):
    if user_name in room_id_map and room_id_map[user_name]:
        return room_id_map[user_name]

    return None


def _find_channel(channels, room_id):
    for key, channel in channels.items():
        room_interval = channel['room_interval']
        if not room_interval is None:
            if room_interval[0] <= int(room_id) <= room_interval[1]:
                return key
    return None


def find_channel_by_user_name(room_id_map, channels, user_name):
    if user_name is None:
        raise AssertionError(
            'User name must be provided.')

    room_id = _find_room_id(room_id_map, str(user_name))

    if room_id is None:
        raise AssertionError('Could not find your seat!')

    channel_name = _find_channel(channels, room_id)

    if channel_name is None:
        raise AssertionError('Could not find your channel')

    return channel_name

def validate_command(channels, action, channel_name=None):
    if not channel_name in channels.keys():
        raise AssertionError(
            'Unsupported channel "{0}"'.format(channel_name))

    if action == Actions.OPEN_30_PERCENT:
        return 'Opening blinds to 30%... ' + channel_name

    if action == Actions.POSITION_TOGGLE:
        return 'Toggling position... ' + channel_name

    if action == Actions.OPEN:
        return 'Opening blinds... ' + channel_name

    if action == Actions.CLOSE:
        return 'Closing blinds... ' + channel_name

    if action == Actions.STOP:
        return 'Stopping current operation...  ' + channel_name

    raise AssertionError('Unsupported action "{0}"'.format(action))

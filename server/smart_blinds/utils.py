import inspect
import json
import unicodedata

from .actions import Actions

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

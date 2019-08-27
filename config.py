CHANNELS = {
    'remote_10_channel1': {
        'label': 'Demo',
        'output_pin': 13,
        'room_interval': (8410, 8419),
        'action_idle': {
            'angle': 1400,
            'sleep': 1
        },
        'action_open': {
            'angle': 900,
            'sleep': 3
        },
        'action_close': {
            'angle': 1800,
            'sleep': 3
        },
    },
}

DATA = 'smart_blinds/data/some_file.json'
DEBUG = False

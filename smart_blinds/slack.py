# -*- coding: utf-8 -*-

from multiprocessing import Process, Queue

import requests

from .utils import (find_channel_by_user_name, get_user_name,
                                logger_message, validate_command)


class Slack(Process):
    def __init__(self, app, room_id_map, channels, smart_blinds, debug_mode, **kwargs):
        super(Slack, self).__init__()

        self.kwargs = kwargs
        self.users = {}

        self.queue = Queue(1)

        self.channels = channels
        self.room_id_map = room_id_map
        self.app = app
        self.smart_blinds = smart_blinds
        self.debug_mode = debug_mode

    def slack_send_message(self, response_url, user_name, message):
        if self.debug_mode:
            print('Response message: ' + message)
            return

        self.app.logger.info(logger_message(
            user_name, response_url))

        slack_response = requests.post(response_url, json={'text': message})

        if slack_response.status_code != 200:
            self.app.logger.error(logger_message(
                user_name, slack_response.text))

    def get_slack_user_email(self, user_name, user_id):
        if user_id in self.users.keys():
            self.app.logger.info(logger_message(
                user_name, 'Using cached slack user email: ' + self.users[user_id]))
            return self.users[user_id]

        self.app.logger.info(logger_message(
            user_name, 'Fetching slack user email'))
        slack_response = requests.get('https://slack.com/api/users.info?token={0}&user={1}'.format(
            self.app.config['SLACK_OAUTH_ACCESS_TOKEN'], user_id))

        if slack_response.status_code != 200:
            self.app.logger.error(logger_message(
                user_name, slack_response.text))
            raise AssertionError('Could not contact Slack API.')

        data = slack_response.json()

        if not data['ok']:
            self.app.logger.error(logger_message(
                user_name, slack_response.text))
            raise AssertionError(
                'Unable to retrieve user data from Slacl API.')

        self.users[user_id] = data['user']['profile']['email']

        return self.users[user_id]

    def command(self, action, channel_name, user_name, user_id):
        user_email = self.get_slack_user_email(user_name, user_id)

        if not user_email:
            pass

        user_name = get_user_name(user_email)

        channel_name = find_channel_by_user_name(
            self.room_id_map, self.channels, user_name)

        self.app.logger.info(logger_message(
            user_email, 'action: {0} channel: {1}'.format(action, channel_name)))

        message = validate_command(self.channels, action, channel_name)
        self.smart_blinds.command(action, channel_name)

        return message

    def try_command(self, action, channel_name, user_name, user_id, response_url):
        try:
            message = self.command(action, channel_name, user_name, user_id)
        except AssertionError as exception:
            message = str(exception)

        self.slack_send_message(response_url, user_name, message)

    def run(self):
        try:
            while True:
                command = self.queue.get()

                action = command['action']
                channel_name = command['channel_name']
                user_name = command['user_name']
                user_id = command['user_id']
                response_url = command['response_url']

                self.try_command(action, channel_name,
                                 user_name, user_id, response_url)

        except KeyboardInterrupt:
            pass

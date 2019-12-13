# -*- coding: utf-8 -*-

import time

import pigpio

from .actions import Actions

MAX_TOGGLE_COUNT = 6
OPEN_TIME_TO_30_PERCENT = 16
CLOSE_TIME_TO_30_PERCENT = 45
TIME_TO_FULL_CLOSE_OPEN = 60
PARTIAL_OPEN_TIMES = 4

class BlindsApi():
    state = Actions.IDLE
    previous_state = None
    toggle_times = 0
    toggle_direction_up = False

    def __init__(self, channel, debug_mode):
        self.channel = channel
        self.servo_pin = self.channel['output_pin']
        self.debug_mode = debug_mode

        if not self.debug_mode:
            self.pigpio_pi = pigpio.pi()
            self.pigpio_pi.set_mode(self.servo_pin, pigpio.OUTPUT)
            self.pigpio_pi.set_PWM_frequency(self.servo_pin, 50)
        else:
            print('[debug] Skipping pigpio init in debug mode')

        self.idle(True)

    def _set_state(self, state):
        if state != Actions.IDLE:
            self.previous_state = self.state
        self.state = state

        if self.debug_mode:
            print('[debug] Set state: {0}'.format(state))

    def _set_angle(self, angle):
        if not self.debug_mode:
            self.pigpio_pi.set_servo_pulsewidth(self.servo_pin, angle)
        else:
            print('[debug] Set angle "{0}" on servo_pin "{1}"'.format(
                angle, self.servo_pin))

        time.sleep(0.2)

    def _command(self, state, angle, sleep=1):
        self._set_state(state)
        self._set_angle(angle)

        if self.debug_mode:
            print('[debug] Sleeping for: {0}'.format(sleep))

        time.sleep(sleep)

        if state != Actions.IDLE:
            self.idle()

    def idle(self, no_sleep=False):
        angle = self.channel['action_idle']['angle']
        sleep = 0 if no_sleep else self.channel['action_idle']['sleep']

        self._command(Actions.IDLE, angle, sleep)

    def can_open():
        if self.state != Actions.IDLE or self.previous_state == Actions.OPEN:
            return False

        return True

    def open(self, sleep=1):
        if self.can_open() == False:
            return

        angle = self.channel['action_open']['angle']
        sleep = self.channel['action_open']['sleep']
        self.toggle_times = 0
        self.toggle_direction_up = False

        self._command(Actions.OPEN, angle, sleep)

    def can_close():
        if self.state != Actions.IDLE or self.previous_state == Actions.CLOSE:
            return False

        return True

    def close(self, sleep=1):
        if self.can_close() == False:
            return

        angle = self.channel['action_close']['angle']
        sleep = self.channel['action_close']['sleep']
        self.toggle_times = 0
        self.toggle_direction_up = True

        self._command(Actions.CLOSE, angle, sleep)

    def can_stop():
        if self.state != Actions.IDLE:
            return False

        return True

    def stop(self):
        if self.can_stop() == False:
            return

        if self.previous_state == Actions.CLOSE:
            angle = self.channel['action_open']['angle']
        elif self.previous_state == Actions.OPEN:
            angle = self.channel['action_close']['angle']
        else:
            angle = self.channel['action_open']['angle']

        self._command(Actions.STOP, angle, 0.2)

    def can_open_partly():
        if self.state != Actions.IDLE:
            return False

        return True

    def open_30_percent(self):
        if self.can_open_partly() == False:
            return

        if self.previous_state == Actions.CLOSE:
            self.open()
            time.sleep(OPEN_TIME_TO_30_PERCENT)
            self.stop()
        elif self.previous_state == Actions.OPEN:
            self.close()
            time.sleep(CLOSE_TIME_TO_30_PERCENT)
            self.stop()
        else:
            self.close()
            time.sleep(TIME_TO_FULL_CLOSE_OPEN)
            self.open()
            time.sleep(OPEN_TIME_TO_30_PERCENT)
            self.stop()

        for _ in range(PARTIAL_OPEN_TIMES):
            self.position_toggle()

    def can_toggle_position():
        if self.state != Actions.IDLE:
            return False

        return True

    def position_toggle(self):
        if self.can_toggle_position() == False:
            return

        if (self.toggle_times >= MAX_TOGGLE_COUNT - 1):
            self.toggle_times = 0
            self.toggle_direction_up = not self.toggle_direction_up
        else:
            self.toggle_times += 1

        if self.toggle_direction_up:
            angle = self.channel['action_open']['angle']
        else:
            angle = self.channel['action_close']['angle']

        self._command(Actions.POSITION_TOGGLE, angle, 0.2)

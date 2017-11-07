"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from jemu_packet import JemuPacket
from jemu_connection import JemuConnection


class JemuGpio:
    _PIN_NUM = "pin_number"
    _TRANSITION_TYPE = "transition_type"

    def __init__(self, jemu_socket_manager):
        self._pin_level_callbacks = []
        self._jemu_socket_manager = jemu_socket_manager

        self._jemu_socket_manager.register(self.receive_packet)

    def on_pin_level_event(self, callbacks):
        self._pin_level_callbacks += callbacks

    def receive_packet(self, jemu_packet):
        for callback in self._pin_level_callbacks:
            callback(jemu_packet[self._PIN_NUM], jemu_packet[self._TRANSITION_TYPE])

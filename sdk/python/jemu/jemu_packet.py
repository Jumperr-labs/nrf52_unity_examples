"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from struct import *

class JemuPacket:
    def __init__(self, packet):
	    (self.__message_type, self.__message_length, self.__message_id, self.__transition_type,
	     self.__pin_number, self.__voltage) = unpack('<iiiiiq', packet)

    def message_type(self):
        return self.__message_type

    def message_length(self):
        return self.__message_length

    def message_id(self):
        return self.__message_id

    def transition_type(self):
        return self.__transition_type

    def pin_number(self):
        return self.__pin_number

    def voltage(self):
        return self.__voltage
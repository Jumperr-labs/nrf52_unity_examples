from threading import Thread
from time import sleep
import socket
import json
import struct
import logging
import sys


class JemuConnection:
    _addr = None
    _port = None
    _conn = None
    _HANDSHAKE = "handshake"
    _COMMAND = "command"
    _COMMAND_TYPE = "command_type"
    _PERIPHERAL_ID = "peripheral_id"
    _TRANSITION_TYPE = "transition_type"
    _PIN_NUM = "pin_number"
    _MESSAGE_ID = "message_id"
    _VOLTAGE = "voltage"
    _API_VERSION = "1"
    _OK = "ok"
    _ERROR = "error"
    _ERROR_CODE = "404"
    _TYPE = "type"
    _RESPONSE = "response"
    _API_V_STRING = "api_version"
    _ERROR_MESSAGE = "error"
    _COMMAND_START = "start"

    _LOG_LEVEL = logging.ERROR
    _logger = logging.getLogger()
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    _logger.addHandler(log_handler)
    _logger.setLevel(_LOG_LEVEL)
    log_handler.setLevel(_LOG_LEVEL)

    def __init__(self, addr, port):
        self._addr = addr
        self._port = port
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn.settimeout(0.3)

        self._callbacks = []
        self._thread = None
        self._should_run = False
        self._shutdown = False

    def start(self):
        self._should_run = True
        self._thread = Thread(target=self.connection_task)
        self._thread.start()

    def close(self):
        self._should_run = False
        while not self._shutdown:
            sleep(0.3)

    def connection_task(self):
        while self._should_run:
            json_buff_string = self.recv_json()
            if json_buff_string is None:
                break
            self._logger.debug("received data: " + json_buff_string)
            json_pack = json.loads(json_buff_string)
            self.inform(json_pack)
        try:
            self._conn.close()
        except socket.error:
            pass
        self._shutdown = True

    def inform(self, jemu_json_packet):
        for callback in self._callbacks:
            callback(jemu_json_packet)

    def register(self, callback):
        self._callbacks.append(callback)

    def connect(self):
        result = False
        try:
            self._conn.connect((self._addr, int(self._port)))
            self._conn.settimeout(0.3)
            result = True
        except:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        finally:
            return result

    def handshake(self):
        self._should_run = True
        self.send_handshake()
        # check response
        response_ack = self.recv_json()
        if response_ack is None:
            return False
        self.check_response(response_ack)
        # send start command
        self.send_start()
        return True

    def check_response(self,response_ack):
        self._logger.debug("handshake response data: " + response_ack)
        response = json.loads(response_ack)
        message_type = response[self._TYPE]
        if message_type != self._RESPONSE:
            raise JemuConnectionException("Error expect response message instead got [" + message_type + "]")
        status_code = response[self._RESPONSE]
        if status_code != self._OK:
            raise JemuConnectionException("Sdk's api version does not match to the jemu's version")

    def send_json(self, json_obj):
        data_to_send = json.dumps(json_obj)
        number_of_bytes = len(data_to_send.encode('utf-8'))
        self._logger.debug("Number of byte of send data: " + str(number_of_bytes))
        number_to_send = struct.pack('!i', number_of_bytes)
        self.send(number_to_send)
        self._logger.debug("Data to send: " + data_to_send)
        self.send(data_to_send)

    def send_handshake(self):
        hand_shake_message = {self._API_V_STRING: self._API_VERSION, self._TYPE: self._HANDSHAKE}
        self.send_json(hand_shake_message)

    def send_start(self):
        ack = {self._TYPE: self._COMMAND, self._COMMAND: self._COMMAND_START}
        self.send_json(ack)

    def send(self, buffer):
        try:
            self._conn.sendall(buffer)
        except socket.error as e:
            raise JemuConnectionException(str(e))

    def recv_json(self):
        data = self.receive(4)
        if data is None:
            return None
        buffer_size = struct.unpack("!i", data)[0]
        self._logger.debug("Number of byte of received data: " + str(buffer_size))
        if buffer_size == 0:
            return None
        return self.receive(buffer_size)

    def receive(self, size):
        ret = b''
        while len(ret) < size:
            try:
                ret += self._conn.recv(size - len(ret))
            except socket.timeout:
                if self._should_run is False:
                    return None
        return ret


class JemuConnectionException(Exception):
    pass

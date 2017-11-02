
class JemuButton:
    __id = None
    __jemu_connection = None
    __LEVEL_HIGH = 1
    __LEVEL_LOW = 0

    _TYPE_STRING = "type"
    _PERIPHERAL_ID = "peripheral_id"
    _PIN_LEVEL = "pin_level"
    _COMMAND = "command"
    _COMMAND_PIN_LOGIC_LEVEL = "set_pin_level"

    def __ButtonGpioJson(self, id, level):
        return {self._PIN_LEVEL: level,
                        self._TYPE_STRING: self._COMMAND,
                        self._PERIPHERAL_ID: id,
                        self._COMMAND: self._COMMAND_PIN_LOGIC_LEVEL}

    def __init__(self, jemu_connection, id):
        self.__id = id
        self.__jemu_connection = jemu_connection

    def On(self):
        self.__jemu_connection.send_json(self.__ButtonGpioJson(self.__id, self.__LEVEL_LOW))

    def Off(self):
        self.__jemu_connection.send_json(self.__ButtonGpioJson(self.__id, self.__LEVEL_HIGH))

    def Status(self):
        return self.__jemu_connection.recv_json()
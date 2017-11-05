from __future__ import print_function
import os
import subprocess
import signal
from time import sleep
from shutil import copyfile
from shutil import copymode
import timeout_decorator

from .jemu_uart import JemuUart
from .jemu_peripherals_parser import JemuPeripheralsParser
from .jemu_button import JemuButton
from .jemu_gpio import JemuGpio
from .jemu_connection import JemuConnection
from .jemu_web_api import JemuWebApi

class EmulationError(Exception):
    pass


class Jemu(object):
    _transpiler_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    _jemu_build_dir = os.path.abspath(os.path.join(_transpiler_dir, 'emulator', '_build'))
    _jemu_bin_src = os.path.join(_jemu_build_dir, 'jemu')

    def __init__(self, working_directory=None):
        self._working_directory = os.path.abspath(working_directory) if working_directory else self._transpiler_dir
        self._jemu_process = None
        self._transpiler_cmd = ["node", "index.js", "--bin", ""]
        self._peripherals_json = os.path.join(self._working_directory, "peripherals.json")
        self._uart_device_path = os.path.join(self._working_directory, 'uart')
        self._jemu_server_address = "localhost"
        self._jemu_server_port = "8000"
        self._jemu_bin = os.path.join(self._working_directory, 'jemu')
        self._uart = None
        self._jemu_gpio = None
        self._jemu_connection = None
        self._peripherals_json_parser =JemuPeripheralsParser(os.path.join(self._working_directory, self._peripherals_json))

        # Use this to get web API functionality instead of local transpiler
        self._web_api = JemuWebApi()

    @property
    def uart(self):
        return self._uart

    @property
    def gpio(self):
        return self._jemu_gpio

    def _build_peripherals_methods(self):
        peripherals = self._peripherals_json_parser.get_buttons()

        for peripheral in peripherals:
            button = JemuButton(self._jemu_connection, peripheral["id"])
            setattr(self, peripheral["name"], button)

    def load(self, file_path):
        #################################################
        # Use this instead to get Web API functionality #
        #################################################
        filename = os.path.basename(file_path)
        emulator_path = os.path.join(os.path.dirname(file_path), '{}.jemu'.format(filename))
        with open(file_path, 'r') as data:
            self._web_api.create_emulator(filename, data, self._jemu_bin)

        # self._transpiler_cmd[3] = self._transpiler_cmd[3] + file_path
        # subprocess.call(self._transpiler_cmd, cwd=self._transpiler_dir, stdout=open(os.devnull, 'w'), stderr=None)
        # copyfile(self._jemu_bin_src, self._jemu_bin)
        # copymode(self._jemu_bin_src, self._jemu_bin)

    def start(self):
        if not os.path.isfile(self._jemu_bin):
            raise Exception(self._jemu_bin + ' is not found')
        elif not os.access(self._jemu_bin, os.X_OK):
            raise Exception(self._jemu_bin + ' is not executable')
        else:
            self._uart = JemuUart(self._uart_device_path)
            self._uart.remove()
            self._jemu_connection = JemuConnection(self._jemu_server_address, self._jemu_server_port)
            self._jemu_gpio = JemuGpio(self._jemu_connection)

            jemu_cmd = self._jemu_bin + " -w"
            self._jemu_process = subprocess.Popen(
                jemu_cmd,
                cwd=self._working_directory,
                shell=True,
                stdin=None,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                close_fds=True,
                preexec_fn=os.setsid
            )
            sleep(0.3)

            @timeout_decorator.timeout(3)
            def wait_for_uart():
                while not os.path.exists(self._uart_device_path):
                    sleep(0.1)

            try:
                wait_for_uart()
            except timeout_decorator.TimeoutError:
                self.stop()
                raise EmulationError

            self._uart.open()


            @timeout_decorator.timeout(3)
            def wait_for_connection():
                while not self._jemu_connection.connect():
                    sleep(0.1)

            try:
                wait_for_connection()
            except timeout_decorator.TimeoutError:
                self.stop()
                raise EmulationError

            if not self._jemu_connection.handshake():
                raise EmulationError

            self._jemu_connection.start()

            self._build_peripherals_methods()

    def stop(self):
        self._jemu_connection.close()
        self._uart.close()
        self._uart.remove()

        if self._jemu_process and self._jemu_process.poll() is None:
            os.killpg(os.getpgid(self._jemu_process.pid), signal.SIGTERM)
            self._jemu_process.wait()

        self._uart = None
        self._jemu_connection = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *err):
        self.stop()

    def __del__(self):
        if os.path.exists(self._jemu_bin):
            os.remove(self._jemu_bin)

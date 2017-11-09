"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function
import os
import subprocess
import signal
import hashlib
from time import sleep
from shutil import copyfile
from shutil import copymode
import json

import timeout_decorator

from .jemu_uart import JemuUart
from .jemu_peripherals_parser import JemuPeripheralsParser
from .jemu_button import JemuButton
from .jemu_gpio import JemuGpio
from .jemu_connection import JemuConnection
from .jemu_web_api import JemuWebApi

DEFAULT_CONFIG = os.path.join(os.path.expanduser('~'), '.jumper', 'config.json')


class EmulationError(Exception):
    pass


class FileNotFoundError(Exception):
    pass


class Jemu(object):
    _transpiler_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    _jemu_build_dir = os.path.abspath(os.path.join(_transpiler_dir, 'emulator', '_build'))
    _jemu_bin_src = os.path.join(_jemu_build_dir, 'jemu')

    def __init__(self, working_directory=None, config_file=None, gdb_mode=False, remote_mode=True):
        self._working_directory = os.path.abspath(working_directory) if working_directory else self._transpiler_dir
        self._remote_mode = remote_mode
        self._gdb_mode = gdb_mode
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
        self._bin_file_sha1_cache_extension = "cache.sha1"
        self._peripherals_json_parser = \
            JemuPeripheralsParser(os.path.join(self._working_directory, self._peripherals_json))

        token = None

        if config_file:
            if not os.path.isfile(config_file):
                raise FileNotFoundError('Config file not found at: {}'.format(os.path.abspath(config_file)))
        else:
            if os.path.isfile(DEFAULT_CONFIG):
                config_file = DEFAULT_CONFIG

        if config_file:
            with open(config_file) as config_data:
                config = json.load(config_data)
            if 'token' in config:
                token = config['token']

        if remote_mode:
            self._web_api = JemuWebApi(jumper_token=token)

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
    
    @staticmethod
    def _get_file_signature(file_path):
        sha1 = hashlib.sha1()

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)

        return sha1.hexdigest()

    def _read_file_signature_backup(self, filename):
        data = ''
        cache_file_location = filename + self._bin_file_sha1_cache_extension
        if os.path.isfile(cache_file_location):
            with open(cache_file_location, 'r') as f:
                data = f.read().replace('\n', '')
        
        return data

    def _write_file_signature_backup(self, sha1_cache_string, filename):
        with open(filename + self._bin_file_sha1_cache_extension, 'w+') as f:
            f.write(sha1_cache_string)

    def load(self, file_path):
        if (self._remote_mode):
            filename = os.path.basename(file_path)
            gen_new = True
            new_signature = self._get_file_signature(file_path)
            
            prev_signature = self._read_file_signature_backup(filename)
            if (prev_signature == new_signature):
                gen_new = False

            self._write_file_signature_backup(new_signature, filename)

            if gen_new:
                with open(file_path, 'r') as data:
                    self._web_api.create_emulator(filename, data, self._jemu_bin)
        else:
            self._transpiler_cmd[3] = self._transpiler_cmd[3] + file_path
            subprocess.call(self._transpiler_cmd, cwd=self._transpiler_dir, stdout=open(os.devnull, 'w'), stderr=None)
            copyfile(self._jemu_bin_src, self._jemu_bin)
            copymode(self._jemu_bin_src, self._jemu_bin)

    def start(self):
        if not os.path.isfile(self._jemu_bin):
            raise Exception(self._jemu_bin + ' is not found')
        elif not os.access(self._jemu_bin, os.X_OK):
            raise Exception(self._jemu_bin + ' is not executable')

        self._uart = JemuUart(self._uart_device_path)
        self._uart.remove()
        self._jemu_connection = JemuConnection(self._jemu_server_address, self._jemu_server_port)
        self._jemu_gpio = JemuGpio(self._jemu_connection)

        jemu_cmd = self._jemu_bin + " -w"
        if self._gdb_mode:
            jemu_cmd += " -g"

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
        pass

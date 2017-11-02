import unittest
import serial
import os
import sys
import subprocess
from time import sleep
from jemu import Jemu

dir = os.path.dirname(os.path.abspath(__file__))
fw_bin = os.path.join(dir, '..', 'pca10040', 'blank', 'armgcc', '_build', 'nrf52832_xxaa.bin')


class TestCLI(unittest.TestCase):
    def setUp(self):
        print(dir)
        self.jemu = Jemu(working_directory=dir)
        print("Generating emulator")
        self.jemu.load(fw_bin)
        print("Finished generating emulator")

    def tearDown(self):
        pass

    def test_sanity(self):
        with self.jemu as j:
            print('Virtual device is running')
            result = j.uart.wait_until_uart_receives('----------------')
            self.assertEqual('FAIL' in result, False)
        
        return True


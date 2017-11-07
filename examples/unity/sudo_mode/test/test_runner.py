import unittest
import serial
import os
import sys
import subprocess
from time import sleep
from jemu import Jemu

dir = os.path.dirname(os.path.abspath(__file__))
fw_bin = os.path.join(dir, '..', 'pca10040', 'blank', 'armgcc', '_build', 'nrf52832_xxaa.bin')


print(dir)
jemu = Jemu(working_directory=dir)
jemu.load(fw_bin)

with jemu as j:
	print('Virtual device is running')
	result = j.uart.wait_until_uart_receives('----------------')        
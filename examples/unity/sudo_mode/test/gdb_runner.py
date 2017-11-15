import os
from jemu import Jemu

dir = os.path.dirname(os.path.abspath(__file__))
fw_bin = os.path.join(dir, '..', 'pca10040', 'blank', 'armgcc', '_build', 'nrf52832_xxaa.bin')
config_file = os.path.join(dir, '..', '..', '..', '..', 'jumper_config.json')

print(dir)
jemu = Jemu(working_directory=dir, config_file=config_file, gdb_mode=True, sudo_mode=True)
jemu.load(fw_bin)

with jemu as j:
    print('Virtual device is running')
    while True:
        j.uart.wait_until_uart_receives('----------------')

import os
from jumper.vlab import Vlab

dir = os.path.dirname(os.path.abspath(__file__))
fw_bin = os.path.join(dir, '..', 'pca10040', 'blank', 'armgcc', '_build', 'nrf52832_xxaa.bin')

print(dir)
vlab = Vlab(working_directory=dir)
vlab.load(fw_bin)

with vlab as v:
    print('Virtual device is running')
    result = v.uart.wait_until_uart_receives('----------------')
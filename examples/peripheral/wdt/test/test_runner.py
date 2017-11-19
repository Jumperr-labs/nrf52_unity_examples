import os
import unittest
from jumper.vlab import Vlab

dir = os.path.dirname(os.path.abspath(__file__))
fw_bin = os.path.join(dir, '..', 'pca10040', 'blank', 'armgcc', '_build', 'nrf52832_xxaa.bin')
# scenario_file1 = ps.path.join(dir, 'scenario_debouncer_signal1.json')
# scenario_file2 = ps.path.join(dir, 'scenario_debouncer_signal2.json')


class TestAppButton(unittest.TestCase):
    def setUp(self):
        self.vlab = Vlab(working_directory=dir)
        self.vlab.load(fw_bin)
        self.did_device_reset = False
        self.vlab.on_interrupt(self.interrupts_listener)
        self.vlab.run_for_ms(500)
        print('Virtual device is running')

    def tearDown(self):
        self.vlab.stop()

    def interrupts_listener(self, interrupt):
        if interrupt.type == jumper.interrupts.RESET:
            self.did_device_reset = True

    def test_should_ignore_button_hold(self):
        self.vlab.button0.on()
        self.vlab.run_for_ms(55)
        self.vlab.button0.off()
        self.vlab.run_for_ms(200)
        self.assertTrue(self.did_device_reset)

    def test_should_respond_to_button_push(self):
        self.vlab.button0.on()
        self.vlab.run_for_ms(45)
        self.vlab.button0.off()
        self.vlab.run_for_ms(200)
        self.assertFalse(self.did_device_reset)


class TestAppDebouncer(unittest.TestCase):
    def setUp(self):
        self.vlab = Vlab(working_directory=dir)
        self.vlab.load(fw_bin)
        self.did_device_reset = False
        self.vlab.on_interrupt(self.interrupts_listener)
        self.vlab.run_for_ms(500)
        print('Virtual device is running')

    def tearDown(self):
        if self.vlab:
            self.vlab.stop()

    def interrupts_listener(self, interrupt):
        if interrupt.type == jumper.interrupts.RESET:
            self.did_device_reset = True

    def test_should_ignore_button_hold(self):
        self.vlab.nrf52.pins[13].signal_generator(type='square', duty_cycle=0.5, frequency=500)
        self.vlab.run_for_ms(1000)
        self.vlab.nrf52.pins[13].set_pin_level(1)
        self.AssertTrue(self.did_device_reset)

    def test_should_respond_to_button_push(self):
        self.vlab.nrf52.pins[13].signal_generator(type='square', duty_cycle=0.5, frequency=50)
        self.vlab.run_for_ms(1000)
        self.vlab.nrf52.pins[13].set_pin_level(1)
        self.AssertFalse(self.did_device_reset)

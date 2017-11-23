import os
import unittest
from jumper.vlab import Vlab
from time import sleep

dir = os.path.dirname(os.path.abspath(__file__))
fw_bin = os.path.join(dir, '..', 'pca10040', 'blank', 'armgcc', '_build', 'nrf52832_xxaa.bin')


class TestAppButton(unittest.TestCase):

    def pins_listener(self, pin_event):
        if pin_event[self.vlab.pin_number] == 17 and pin_event[self.vlab.pin_level] == 0:
            self.is_led_on = True

    def setUp(self):
        self.vlab = Vlab(working_directory=dir)
        self.vlab.load(fw_bin)
        self.vlab.on_pin_level_event(self.pins_listener)
        self.vlab.run_for_ms(500)
        print('Virtual device is running')
        self.is_led_on = False

    def tearDown(self):
        self.vlab.stop()

    def test_should_ignore_button_noise(self):
        self.vlab.BUTTON1.on()
        self.vlab.run_for_ms(1)
        self.vlab.BUTTON1.off()
        self.vlab.run_for_ms(500)
        self.assertFalse(self.is_led_on)

    def test_led_should_turn_on_on_button_push(self):
        self.vlab.BUTTON1.on()
        self.vlab.run_for_ms(60)
        self.vlab.BUTTON1.off()
        self.vlab.run_for_ms(500)
        self.assertTrue(self.is_led_on)
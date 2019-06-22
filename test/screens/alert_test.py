import unittest

from bms import bq
from bms.screens.alert import AlertScreen
from test.mock_controller import MockController
from test.states.mock_machine import MockStatemachine


class AlertScreenTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.sm = MockStatemachine(self.controller)
        self.display = self.controller.display
        self.rotary = self.controller.rotary
        self.screen = AlertScreen(self.controller)

    def test_bq_faults(self):
        self.controller.bq.faults = [bq.OCD, bq.SCD, bq.OV, bq.UV, bq.OVRD_ALERT, bq.DEVICE_XREADY]

        self.screen.enter()
        # self.display.print_buffer()
        self.assertEqual("ALERT", self.display.drawn_text[0][0])
        self.assertEqual("Discharge Overcurrent", self.display.drawn_text[1][0])
        self.assertEqual("Dischg Short Circuit", self.display.drawn_text[2][0])
        self.assertEqual("Overvoltage", self.display.drawn_text[3][0])
        self.assertEqual("Undervoltage", self.display.drawn_text[4][0])
        self.assertEqual("Alert Pin Override", self.display.drawn_text[5][0])
        self.assertEqual("Device Not Ready", self.display.drawn_text[6][0])
        self.assertEqual("Click to Resume", self.display.drawn_text[7][0])

    def test_click_to_resume(self):
        self.controller.bq.faults = [bq.OCD]

        self.screen.enter()
        self.controller.rotary.clicked = True
        self.screen.user_input()

        self.assertEqual("clear", self.controller.sm.last_event)

    def test_custom_fault(self):
        self.controller.alert_msg = "Cake is so Delicious"
        self.screen.enter()
        # self.display.print_buffer()
        self.assertEqual("ALERT", self.display.drawn_text[0][0])
        self.assertEqual("Cake is so Delicious", self.display.drawn_text[1][0])





import unittest

from bms.screens.prechg import PrechargeScreen
from test.mock_controller import MockController
from test.states.mock_machine import MockStatemachine


class PrechgScreenTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.sm = MockStatemachine(self.controller)
        self.display = self.controller.display
        self.rotary = self.controller.rotary
        self.screen = PrechargeScreen(self.controller)

    def test_enter(self):
        self.controller.bq.batt_voltage_value = 22.2
        self.screen.enter()
        # self.display.print_buffer()
        self.assertEqual("Pre-Charging", self.display.drawn_text[0][0])
        self.assertEqual("Battery V:", self.display.drawn_text[1][0])
        self.assertEqual("22.2", self.display.drawn_text[2][0])

    def test_click_enters_menu(self):
        controller = self.controller
        controller.rotary.clicked = True
        self.screen.user_input()
        self.assertEqual(controller.main_menu, controller.screen)

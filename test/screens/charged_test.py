import unittest

from bms.screens.charged import ChargedScreen
from test.mock_controller import MockController
from test.states.mock_machine import MockStatemachine


class ChargedScreenTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.sm = MockStatemachine(self.controller)
        self.display = self.controller.display
        self.rotary = self.controller.rotary
        self.screen = ChargedScreen(self.controller)

    def test_enter(self):
        self.screen.enter()
        # self.display.print_buffer()
        self.assertEqual("Battery Fully Charged", self.display.drawn_text[0][0])

    def test_click_enters_menu(self):
        controller = self.controller
        controller.rotary.clicked = True
        self.screen.user_input()
        self.assertEqual(controller.main_menu, controller.screen)
import unittest

from bms.screens.low_v import LowVScreen
from test.mock_controller import MockController


class LowVScreenTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.display = self.controller.display
        self.bq = self.controller.bq
        self.cells = self.controller.cells
        self.screen = LowVScreen(self.controller)

    def test_click_enters_menu(self):
        boss = self.controller
        boss.rotary.clicked = True
        self.screen.user_input()
        self.assertEqual(boss.main_menu, boss.screen)

    def test_text(self):
        self.screen.enter()
        # self.display.print_buffer()
        self.assertEqual("Please Charge Me!", self.display.drawn_text[0][0])
        self.assertEqual("Pack V:", self.display.drawn_text[1][0])

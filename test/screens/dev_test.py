import unittest

from bms.screens.dev import DevScreen
from test.mock_controller import MockController


class DevScreenTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.display = self.controller.display
        self.bq = self.controller.bq
        self.cells = self.controller.cells
        self.screen = DevScreen(self.controller)

    def test_click_enters_menu(self):
        boss = self.controller
        boss.rotary.clicked = True
        self.screen.user_input()
        self.assertEqual(boss.main_menu, boss.screen)

    def test_menu_itemness(self):
        self.controller.screen = None
        self.assertEqual("Developer Info", self.screen.menu_name())
        self.screen.menu_sel()
        self.assertEqual(self.screen, self.controller.screen)

    def test_enter(self):
        self.screen.enter()

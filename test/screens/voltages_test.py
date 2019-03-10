import unittest

from bms.screens.voltages import VoltagesScreen
from test.mock_controller import MockController


class VoltagesScreenTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.display = self.controller.display
        self.bq = self.controller.bq
        self.cells = self.controller.cells
        self.screen = VoltagesScreen(self.controller)

    def test_click_enters_menu(self):
        boss = self.controller
        boss.rotary.clicked = True
        self.screen.update()
        self.assertEqual(boss.main_menu, boss.screen)

    def test_menu_itemness(self):
        self.controller.screen = None
        self.assertEqual("Cell Voltages", self.screen.menu_name())
        self.screen.menu_sel()
        self.assertEqual(self.screen, self.controller.screen)

    def test_enter(self):
        self.screen.enter()
        self.assertEqual(9, len(self.screen.display_cells))


import unittest

from bms.screens.bargraph import BargraphScreen
from test.mock_controller import MockController


class HomeTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.display = self.controller.display
        self.bq = self.controller.bq
        self.cells = self.controller.cells
        self.home = BargraphScreen(self.controller)


    def test_enter_and_update(self):
        for i in range(self.cells.count):
            self.cells[i].voltage = 2.7 + i/10

        home = self.home
        home.enter()
        home.update()

        # self.display.print_buffer()

    def test_click_enters_menu(self):
        boss = self.controller
        boss.rotary.clicked = True
        self.home.update()
        self.assertEqual(boss.main_menu, boss.screen)




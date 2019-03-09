import unittest

from bms.screens.home import HomeScreen
from test.mock_controller import MockController


class HomeTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.display = self.controller.display
        self.bq = self.controller.bq
        self.cells = self.controller.cells


    def test_enter_and_update(self):
        for i in range(self.cells.count):
            self.cells[i].voltage = 2.7 + i/10

        home = HomeScreen(self.controller)
        home.enter()
        home.update()

        # self.display.print_buffer()




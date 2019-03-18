import unittest

from bms.screens.error import ErrorScreen
from test.mock_controller import MockController


class ErrorScreenTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.display = self.controller.display
        self.rotary = self.controller.rotary
        self.screen = ErrorScreen(self.controller)

    def test_with_trace(self):
        trace = ["Traceback (most recent call last):",
                 "  File \"bms/flexbms.py\", line 65, in main",
                 "  File \"bms/controller.py\", line 39, in setup",
                 "  File \"bms/bq.py\", line 230, in setup",
                 "  File \"bms/bq.py\", line 230, in setup",
                 "RuntimeError: BQ address not found in scan"]
        trace.reverse()
        self.screen.trace_lines = trace
        self.screen.enter()
        # self.display.print_buffer()
        self.assertEqual("ERROR", self.display.drawn_text[0][0])
        self.assertEqual("RuntimeError: BQ addr", self.display.drawn_text[1][0])
        self.assertEqual("ess not found in scan", self.display.drawn_text[2][0])
        self.assertEqual("File \"bms/bq.py\", lin", self.display.drawn_text[3][0])
        self.assertEqual("e 230, in setup", self.display.drawn_text[4][0])
        self.assertEqual("File \"bms/bq.py\", lin", self.display.drawn_text[5][0])
        self.assertEqual("e 230, in setup", self.display.drawn_text[6][0])
        self.assertEqual("File \"bms/controller.", self.display.drawn_text[7][0])

    def test_with_no_trace(self):
        self.screen.enter()
        # self.display.print_buffer()
        self.assertEqual("ERROR", self.display.drawn_text[0][0])
        self.assertEqual("Could not read", self.display.drawn_text[1][0])
        self.assertEqual("/error.txt", self.display.drawn_text[2][0])

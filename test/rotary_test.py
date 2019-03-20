import unittest

from bms.rotary import Rotary
from test.mock_pins import MockDPin


class MockEncoder:
    def __init__(self):
        self.position = 0


class RotaryTest(unittest.TestCase):

    def setUp(self):
        # self.encoder = MockEncoder()
        self.dt = MockDPin()
        self.clk = MockDPin()
        self.rotary = Rotary(self.dt, self.clk)

    def test_creation(self):
        self.assertEqual(self.dt, self.rotary.dt)
        self.assertEqual(self.clk, self.rotary.clk)

    def test_has_update_when_position_changes(self):
        self.assertEqual(False, self.rotary.has_update())
        # self.encoder.position = 1
        self.rotary.handle_rotate()
        self.assertEqual(True, self.rotary.has_update())

    def test_had_update_when_clicked(self):
        self.assertEqual(False, self.rotary.has_update())
        self.rotary.handle_click()
        self.assertEqual(True, self.rotary.has_update())

    def test_doesnt_have_update_when_rested(self):
        self.rotary.handle_click()
        self.assertEqual(True, self.rotary.has_update())
        self.rotary.rest()
        self.assertEqual(False, self.rotary.has_update())

    def test_position_change(self):
        self.rotary.pos = -5
        self.rotary.rest()

        self.assertEqual(0, self.rotary.get_rel_pos())
        self.rotary.pos = -4
        self.assertEqual(1, self.rotary.get_rel_pos())
        self.rotary.pos = 0
        self.assertEqual(5, self.rotary.get_rel_pos())
        self.rotary.pos = -6
        self.assertEqual(-1, self.rotary.get_rel_pos())

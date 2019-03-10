import unittest

from bms.rotary import Rotary


class MockEncoder:
    def __init__(self):
        self.position = 0


class RotaryTest(unittest.TestCase):

    def setUp(self):
        self.encoder = MockEncoder()
        self.rotary = Rotary(self.encoder)

    def test_creation(self):
        self.assertEqual(self.encoder, self.rotary.encoder)

    def test_has_update_when_position_changes(self):
        self.assertEqual(False, self.rotary.has_update())
        self.encoder.position = 1
        self.assertEqual(True, self.rotary.has_update())

    def test_had_update_when_clicked(self):
        self.assertEqual(False, self.rotary.has_update())
        self.rotary.click()
        self.assertEqual(True, self.rotary.has_update())

    def test_doesnt_have_update_when_rested(self):
        self.rotary.click()
        self.assertEqual(True, self.rotary.has_update())
        self.rotary.rest()
        self.assertEqual(False, self.rotary.has_update())

    def test_position_change(self):
        self.encoder.position = -5
        self.rotary.rest()

        self.assertEqual(0, self.rotary.get_rel_pos())
        self.encoder.position = -4
        self.assertEqual(1, self.rotary.get_rel_pos())
        self.encoder.position = 0
        self.assertEqual(5, self.rotary.get_rel_pos())
        self.encoder.position = -6
        self.assertEqual(-1, self.rotary.get_rel_pos())

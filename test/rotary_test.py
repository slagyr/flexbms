import unittest

from bms.rotary import Rotary
from test.mock_pin import MockPin


class MockEncoder:
    def __init__(self):
        self.position = 0


class RotaryTest(unittest.TestCase):

    def setUp(self):
        self.encoder = MockEncoder()
        self.rotary = Rotary(self.encoder)

    def test_creation(self):
        self.assertEqual(self.encoder, self.rotary.encoder)

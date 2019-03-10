from bms.rotary import Rotary
from test.rotary_test import MockEncoder


class MockRotary(Rotary):
    def __init__(self):
        super().__init__(MockEncoder())
from bms.rotary import Rotary
from test.rotary_test import MockEncoder


class MockRotary(Rotary):
    def __init__(self):
        super().__init__(MockEncoder())
        self.was_setup = False
        self.was_rested = False
        self.rel_pos = 0

    def setup(self):
        self.was_setup = True

    def has_update(self):
        return self.clicked or self.rel_pos != 0

    def get_rel_pos(self):
        return self.rel_pos

    def rest(self):
        self.was_rested = True


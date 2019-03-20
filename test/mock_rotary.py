from bms.rotary import Rotary
from test.mock_pins import MockPin


class MockRotary(Rotary):
    def __init__(self):
        super().__init__(MockPin(), MockPin())
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


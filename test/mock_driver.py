from bms.driver import Driver
from test.mock_pins import MockAPin, MockDPin


class MockDriver(Driver):

    def __init__(self):
        super().__init__(MockDPin(), MockDPin(), MockDPin(), MockAPin())
        self.was_setup = False

    def setup(self):
        super().setup()
        self.was_setup = True


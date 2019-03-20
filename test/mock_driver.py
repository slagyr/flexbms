from bms.driver import Driver
from test.mock_pins import MockADC, MockPin


class MockDriver(Driver):

    def __init__(self):
        super().__init__(MockPin(), MockPin(), MockPin(), MockADC())
        self.was_setup = False

    def setup(self):
        super().setup()
        self.was_setup = True


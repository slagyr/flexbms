from bms.driver import Driver
from test.mock_pins import MockADC, MockPin


class MockDriver(Driver):

    def __init__(self):
        super().__init__(MockPin(), MockPin(), MockPin(), MockADC())
        self.was_setup = False
        self.pack_voltage_value = None

    def setup(self):
        super().setup()
        self.was_setup = True

    def pack_voltage(self):
        if self.pack_voltage_value:
            return self.pack_voltage_value
        else:
            return super().pack_voltage()




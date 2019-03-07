from bms.cells import Cells
from test.mock import Mock

class MockCells(Mock):
    def __init__(self):
        idol = Cells("bq", 9)
        self.was_setup = False
        self.was_updated = False
        self.voltages = idol.voltages
        self.ids = idol.ids
        self.count = idol.count
        self.bq = "bq"
        self.assert_mock(idol)

    def setup(self):
        self.was_setup = True

    def update_voltages(self):
        self.was_updated = True

    def soc(self, i):
        return 0.5 + i/100
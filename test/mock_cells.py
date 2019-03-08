from bms.cells import Cells

class MockCells(Cells):
    def __init__(self, bq, count):
        super().__init__(bq, count)
        self.was_setup = False
        self.was_updated = False

    def setup(self):
        super().setup()
        self.was_setup = True

    def update_voltages(self):
        super().update_voltages()
        self.was_updated = True


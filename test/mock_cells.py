from bms.cells import Cells

class MockCells(Cells):
    def __init__(self, count):
        super().__init__(count)
        self.was_setup = False
        self.balancing_updated = False

    def setup(self):
        super().setup()
        self.was_setup = True

    def update_balancing(self, bq):
        self.balancing_updated = True




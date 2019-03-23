from bms.cells import Cells

class MockCells(Cells):
    def __init__(self, count):
        super().__init__(count)
        self.was_setup = False
        self.was_balancing_updated = False
        self.was_balancing_reset = False
        for cell in self:
            cell.voltage = 3.6

    def setup(self):
        super().setup()
        self.was_setup = True

    def update_balancing(self, bq):
        self.was_balancing_updated = True

    def reset_balancing(self, bq):
        super().reset_balancing(bq)
        self.was_balancing_reset = True






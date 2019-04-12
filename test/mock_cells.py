from bms.cells import Cells

class MockCells(Cells):
    def __init__(self, bq, count):
        super().__init__(bq, count)
        self.was_setup = False
        self.was_balancing_updated = False
        self.was_balancing_reset = False
        for cell in self:
            cell.voltage = 3.6

    def setup(self):
        super().setup()
        self.was_setup = True

    def update_balancing(self):
        self.was_balancing_updated = True

    def reset_balancing(self):
        super().reset_balancing()
        self.was_balancing_reset = True






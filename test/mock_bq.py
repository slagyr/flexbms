from bms.bq import BQ
from test.mock_bq_i2c import MockBqI2C


class MockBQ(BQ):
    def __init__(self):
        super().__init__(MockBqI2C())
        self.voltages_loaded = False
        self.was_setup = False
        self.balancing_cells = []
        self.alert_processed = False
        self.voltages = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]

    def setup(self):
        self.was_setup = True

    def cell_voltage(self, id):
        return self.voltages[id - 1]

    def batt_voltage(self):
        return 42

    def set_balance_cells(self, cell_ids):
        self.balancing_cells = cell_ids

    def is_cell_balancing(self, id):
        return False

    def set_balance_cell(self, id, on):
        if on and id not in self.balancing_cells:
            self.balancing_cells.append(id)
        if not on and id in self.balancing_cells:
            self.balancing_cells.remove(id)

    def load_cell_voltages(self, cells):
        self.voltages_loaded = True

    def process_alert(self):
        super().process_alert()
        self.alert_processed = True



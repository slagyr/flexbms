from bms.bq import BQ
from test.mock_bq_i2c import MockBqI2C
from test.mock_conf import MockConfig


class MockBQ(BQ):
    def __init__(self, conf=MockConfig()):
        super().__init__(conf, MockBqI2C())
        self.voltages_loaded = False
        self.was_setup = False
        self.balancing_cells = []
        self.alert_processed = False
        self.stub_batt_v = 42
        self.stub_voltages = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
        self.stub_therms = [10000, 10000, 10000]
        self.was_sys_stat_cleared = False

    def setup(self):
        self.was_setup = True

    def cell_voltage(self, id):
        return self.stub_voltages[id - 1]

    def batt_voltage(self):
        return self.stub_batt_v

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

    def therm_r(self, id):
        return self.stub_therms[id]

    def clear_sys_stat(self):
        super().clear_sys_stat()
        self.was_sys_stat_cleared = True










import unittest

from bms.states.eval import EvalState
from test.states.mock_machine import MockStatemachine


class EvalStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.controller.setup()
        self.state = EvalState(self.sm)

        for cell in self.controller.cells:
            cell.voltage = 3.6

    def test_entry_turns_off_fets(self):
        bq = self.controller.bq
        bq.discharge(True)
        bq.charge(True)

        self.state.enter()

        self.assertEqual(False, bq.discharge())
        self.assertEqual(False, bq.charge())

    def test_sets_tick_interval(self):
        self.state.enter()
        self.assertEqual(500, self.controller.sm_tick_interval())

    def test_voltages_are_loaded(self):
        self.state.tick()

        self.assertEqual(True, self.controller.bq.voltages_loaded)
        
    def test_low_voltage_detected(self):
        self.controller.cells[5].voltage = 2.4

        self.state.tick()

        self.assertEqual("low_v", self.sm.last_event)

    def test_charge_power_detected(self):
        driver = self.controller.driver
        driver.stub_pack_v = self.controller.cells.max_serial_voltage()

        self.state.tick()

        self.assertEqual("pow_on", self.sm.last_event)
        
    def test_normal_voltage(self):
        self.state.tick()

        self.assertEqual("norm_v", self.sm.last_event)

    def test_logs_pack_info_on_tick(self):
        self.state.tick()
        self.assertEqual(1, len(self.controller.logger.pack_log))

    def test_logs_cells_on_tick(self):
        self.state.tick()
        self.assertEqual(1, len(self.controller.logger.cell_log))

    def test_logs_temps_on_tick(self):
        self.state.tick()
        self.assertEqual(1, len(self.controller.logger.temp_log))







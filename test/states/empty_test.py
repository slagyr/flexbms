import unittest

from bms.states.empty import EmptyState
from test.states.mock_machine import MockStatemachine


class EmptyStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.controller.setup()
        self.state = EmptyState(self.sm)

    def test_entry_turns_off_everything(self):
        bq = self.controller.bq
        driver = self.controller.driver
        bq.discharge(True)
        bq.charge(True)
        bq.adc(True)
        bq.cc(True)
        driver.chargepump(True)
        driver.packmonitor(True)
        driver.precharge(True)

        self.state.enter()

        self.assertEqual(False, bq.discharge())
        self.assertEqual(False, bq.charge())
        self.assertEqual(False, bq.adc())
        self.assertEqual(False, bq.cc())
        self.assertEqual(False, driver.chargepump())
        self.assertEqual(False, driver.packmonitor())
        self.assertEqual(False, driver.precharge())
        
    def test_sets_tick_interval(self):
        self.state.enter()
        self.assertEqual(100, self.controller.sm_tick_interval())
        
    def test_tick_wakes_to_check_voltage(self):
        bq = self.controller.bq
        self.state.enter()
        self.controller.screen_outdated(False)

        self.state.tick()
        self.assertEqual(False, bq.voltages_loaded)
        self.assertEqual(True, self.state.in_wake_cycle)
        self.assertEqual(True, bq.adc())
        self.assertEqual(500, self.controller.sm_tick_interval())

        self.state.tick()
        self.assertEqual(True, bq.voltages_loaded)
        self.assertEqual(False, self.state.in_wake_cycle)
        self.assertEqual(False, bq.adc())
        self.assertEqual(10000, self.controller.sm_tick_interval())

    def test_pow_on_when_pack_v_is_high(self):
        bq = self.controller.bq
        pack = self.controller.pack
        cells = self.controller.cells
        pack.stub_pack_v = cells.max_serial_voltage() + 0.5
        pack.stub_batt_v = cells.max_serial_voltage() / 2

        self.state.enter()
        self.state.tick()
        self.state.tick()
        self.assertEqual(True, bq.voltages_loaded)
        self.assertEqual("pow_on", self.sm.last_event)

    def test_logs_pack_info_on_wake_tick(self):
        self.state.tick()
        self.state.tick()
        self.assertEqual(1, self.controller.logger.count_log_type("pack:"))

    def test_logs_cells_on_wake_tick(self):
        self.state.tick()
        self.state.tick()
        self.assertEqual(1, self.controller.logger.count_log_type("cells:"))

    def test_logs_temps_on_wake_tick(self):
        self.state.tick()
        self.state.tick()
        self.assertEqual(1, self.controller.logger.count_log_type("temps:"))


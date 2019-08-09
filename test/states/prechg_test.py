import unittest

from bms.states.prechg import PreChgState
from test.states.mock_machine import MockStatemachine


class PreChgStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.controller.setup()
        self.state = PreChgState(self.sm)

        cells = self.controller.cells
        pack = self.controller.pack
        pack.stub_pack_v = cells.max_serial_voltage()
        for cell in cells:
            cell.voltage = 2.0
        pack.stub_batt_v = 18.0

    def test_entry_turns_stuff_on(self):
        bq = self.controller.bq
        driver = self.controller.driver
        bq.discharge(False)
        bq.charge(True)
        bq.adc(True)
        driver.chargepump(False)
        driver.precharge(False)

        self.state.enter()

        self.assertEqual(True, bq.discharge())
        self.assertEqual(False, bq.charge())
        self.assertEqual(True, bq.adc())
        self.assertEqual(True, driver.chargepump())
        self.assertEqual(True, driver.precharge())

    def test_sets_tick_interval(self):
        self.state.enter()
        self.assertEqual(500, self.controller.sm_tick_interval())
        
    def test_remains_in_prechage_while_cells_remain_low(self):
        self.state.enter()
        
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

    def test_pow_off_event_when_charger_unplugged(self):
        pack = self.controller.pack

        self.state.enter()
        pack.stub_pack_v = 5
        self.state.tick()
        self.assertEqual("pow_off", self.sm.last_event)

    def test_norm_v_when_cells_rise(self):
        cells = self.controller.cells
        self.state.enter()
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

        for cell in cells:
            cell.voltage = 2.6
        cells[5].voltage = 2.4
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

        cells[5].voltage = 2.6
        self.state.tick()
        self.assertEqual("norm_v", self.sm.last_event)

    def test_logs_pack_info_on_tick(self):
        self.state.tick()
        self.assertEqual(1, self.controller.logger.count_log_type("pack:"))

    def test_logs_cells_on_tick(self):
        self.state.tick()
        self.assertEqual(1, self.controller.logger.count_log_type("cells:"))

    def test_logs_temps_on_tick(self):
        self.state.tick()
        self.assertEqual(1, self.controller.logger.count_log_type("temps:"))


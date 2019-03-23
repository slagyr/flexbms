import unittest

from bms.states.prechg import PreChgState
from test.states.mock_machine import MockStatemachine


class PreChgStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.state = PreChgState(self.sm)

        cells = self.controller.cells
        self.controller.driver.pack_voltage_value = cells.max_serial_voltage()
        for cell in cells:
            cell.voltage = 2.0
        self.controller.bq.batt_voltage_value = 18.0

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

    def test_entry_sets_home_screen_to_alertscreen(self):
        self.state.enter()
        self.assertEqual(self.controller.prechg_screen, self.controller.home_screen)
        
    def test_remains_in_prechage_while_cells_remain_low(self):
        self.state.enter()
        
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

    def test_pow_off_event_when_charger_unplugged(self):
        driver = self.controller.driver

        self.state.enter()
        driver.pack_voltage_value = 5
        self.state.tick()
        self.assertEqual("pow_off", self.sm.last_event)

    def test_norm_v_when_cells_rise(self):
        driver = self.controller.driver
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

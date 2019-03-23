import unittest

from bms.states.full import FullState
from test.states.mock_machine import MockStatemachine


class FullStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.state = FullState(self.sm)

        for cell in self.controller.cells:
            cell.voltage = 4.2

    def test_entry_turns_stuff_on(self):
        bq = self.controller.bq
        driver = self.controller.driver
        bq.discharge(True)
        bq.charge(True)
        bq.adc(False)
        driver.chargepump(False)
        driver.precharge(True)

        self.state.enter()

        self.assertEqual(False, bq.discharge())
        self.assertEqual(False, bq.charge())
        self.assertEqual(True, bq.adc())
        self.assertEqual(True, driver.chargepump())
        self.assertEqual(False, driver.precharge())

    def test_sets_tick_interval(self):
        self.state.enter()
        self.assertEqual(500, self.controller.sm_tick_interval())

    def test_entry_sets_home_screen_to_alertscreen(self):
        self.state.enter()
        self.assertEqual(self.controller.charged_screen, self.controller.home_screen)

    def test_nothing_happens_when_cells_stay_full(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.batt_voltage_value = cells.max_serial_voltage()
        driver.pack_voltage_value = cells.max_serial_voltage()

        self.state.enter()
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)
        
    def test_voltage_drop_goes_back_to_charge(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.batt_voltage_value = cells.max_serial_voltage()
        driver.pack_voltage_value = cells.max_serial_voltage()
        self.state.enter()

        cells[5].voltage = 4.18
        self.state.tick()
        self.assertEqual("norm_v", self.sm.last_event)

    def test_pow_off_event_when_charger_unplugged(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.batt_voltage_value = cells.max_serial_voltage()
        driver.pack_voltage_value = cells.max_serial_voltage()

        self.state.enter()
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

        driver.pack_voltage_value = 29
        self.state.tick()
        self.assertEqual("pow_off", self.sm.last_event)



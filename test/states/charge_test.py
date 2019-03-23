import unittest

from bms.states.charge import ChargeState
from test.states.mock_machine import MockStatemachine


class ChargeStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.state = ChargeState(self.sm)

    def test_entry_turns_stuff_on(self):
        bq = self.controller.bq
        driver = self.controller.driver
        bq.discharge(False)
        bq.charge(False)
        bq.adc(False)
        driver.chargepump(False)
        driver.precharge(False)

        self.state.enter()

        self.assertEqual(True, bq.discharge())
        self.assertEqual(True, bq.charge())
        self.assertEqual(True, bq.adc())
        self.assertEqual(True, driver.chargepump())
        self.assertEqual(False, driver.precharge())

    def test_sets_tick_interval(self):
        self.state.enter()
        self.assertEqual(500, self.controller.sm_tick_interval())

    def test_entry_sets_home_screen_to_alertscreen(self):
        self.state.enter()
        self.assertEqual(self.controller.voltages_screen, self.controller.home_screen)

    def test_low_V_triggers_event(self):
        self.state.enter()
        self.controller.cells[5].voltage = 1.1

        for i in range(10):
            self.state.tick()
        self.assertEqual("low_v", self.sm.last_event)

    def test_pow_off_event_when_charger_unplugged(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.batt_voltage_value = 30.0
        driver.pack_voltage_value = cells.max_serial_voltage()

        self.state.enter()
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

        driver.pack_voltage_value = 29
        self.state.tick()
        self.assertEqual("pow_off", self.sm.last_event)
        
    def test_charge_overcurrent(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.batt_voltage_value = 30.0
        driver.pack_voltage_value = cells.max_serial_voltage()

        bq.amperage = 1.5
        self.state.enter()
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

        bq.amperage = 1.511
        self.state.enter()
        self.state.tick()
        self.assertEqual("alert", self.sm.last_event)
        self.assertEqual("Charge Overcurrent", self.controller.alert_msg)

    def test_balance_disabled_on_exit(self):
        self.state.exit()
        self.assertEqual(True, self.controller.cells.was_balancing_reset)
        
    def test_balance_schedule(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.batt_voltage_value = 30.0
        driver.pack_voltage_value = cells.max_serial_voltage()

        self.state.enter()
        self.assertEqual(False, cells.was_balancing_updated)
        self.assertEqual(False, cells.was_balancing_reset)
        self.assertEqual(0, self.state.balance_counter)

        self.state.tick()
        self.assertEqual(True, cells.was_balancing_updated)
        self.assertEqual(False, cells.was_balancing_reset)
        self.assertEqual(1, self.state.balance_counter)

        cells.was_balancing_updated = False
        for i in range(59): # 30 seconds
            self.state.tick()
            self.assertEqual(False, cells.was_balancing_updated)
            self.assertEqual(False, cells.was_balancing_reset)

        self.state.tick()
        self.assertEqual(False, cells.was_balancing_updated)
        self.assertEqual(True, cells.was_balancing_reset)

        cells.was_balancing_reset = False
        for i in range(6): # 3 seconds
            self.state.tick()
            self.assertEqual(False, cells.was_balancing_updated)
            self.assertEqual(False, cells.was_balancing_reset)
        self.assertEqual(0, self.state.balance_counter)
        
    def test_full_v_event_when_fully_charged(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        driver.pack_voltage_value = cells.max_serial_voltage()
        bq.batt_voltage_value = cells.max_serial_voltage()
        for cell in cells:
            cell.voltage = 4.2

        self.state.enter()
        self.state.tick()
        self.assertEqual("full_v", self.sm.last_event)

    def test_CHG_FET_off_to_balance_off_full_cells(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        driver.pack_voltage_value = cells.max_serial_voltage()
        bq.batt_voltage_value = cells.max_serial_voltage()
        self.state.enter()

        for cell in cells:
            cell.voltage = 4.0
        cells[5].voltage = 4.21  # need to turn off CHG FET to prevent OV

        self.state.tick()
        self.assertEqual(False, bq.charge())

        cells[5].voltage = 4.0  # balanced to lower V
        for i in range(67): # enough ticks to get counter back to 0
            self.state.tick()
        self.assertEqual(True, bq.charge())

    def test_incorrect_charge_voltage_on_enter(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.charge(False)
        driver.pack_voltage_value = 86
        bq.batt_voltage_value = cells.max_serial_voltage()
        self.state.enter()
        
        self.assertEqual("alert", self.sm.last_event)
        self.assertEqual("Wrong Charge V: 86.0", self.controller.alert_msg)
        self.assertEqual(False, bq.charge())

    def test_incorrect_charge_voltage_on_tick(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.charge(False)
        driver.pack_voltage_value = cells.max_serial_voltage()
        bq.batt_voltage_value = cells.max_serial_voltage()
        self.state.enter()
        self.assertEqual(True, bq.charge())

        driver.pack_voltage_value = cells.max_serial_voltage() + 0.6
        self.state.tick()
        self.assertEqual("alert", self.sm.last_event)
        self.assertEqual("Wrong Charge V: 38.4", self.controller.alert_msg)





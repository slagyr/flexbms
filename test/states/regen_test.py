import unittest

from bms.states.regen import RegenState
from test.states.mock_machine import MockStatemachine


class RegenStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.conf = self.controller.conf
        self.state = RegenState(self.sm)

        self.controller.setup()
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.amps_in = 1.5
        bq.stub_batt_v = 30.0
        driver.stub_pack_v = cells.max_serial_voltage()
        bq.stub_batt_v = cells.max_serial_voltage()

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

    # def test_low_V_triggers_event(self):
    #     self.state.enter()
    #     self.controller.cells[5].voltage = 1.1
    #
    #     for i in range(10):
    #         self.state.tick()
    #     self.assertEqual("low_v", self.sm.last_event)

    def test_pow_off_event_when_regen_power_dies(self):
        pack = self.controller.pack
        cells = self.controller.cells
        self.state.enter()
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

        pack.stub_batt_v = 36.0
        pack.stub_pack_v = 35.0

        self.state.tick()
        self.assertEqual("pow_off", self.sm.last_event)

    def test_charge_overcurrent(self):
        self.state.enter()
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

        self.controller.pack.expire()
        self.controller.bq.amps_in = 1.56

        self.state.enter()
        self.state.tick()
        self.assertEqual("alert", self.sm.last_event)
        self.assertEqual("Charge Overcurrent", self.controller.alert_msg)

    def test_doesnt_charge_when_any_cell_full(self):
        bq = self.controller.bq
        cells = self.controller.cells
        cells[5].voltage = 4.2

        self.state.enter()
        self.state.tick()

        self.assertEqual(False, bq.charge())

    # def test_incorrect_charge_voltage_on_enter(self):
    #     driver = self.controller.driver
    #     bq = self.controller.bq
    #     bq.charge(False)
    #     driver.stub_pack_v = 86
    #     self.state.enter()
    #
    #     self.assertEqual("alert", self.sm.last_event)
    #     self.assertEqual("Wrong Charge V: 86.0", self.controller.alert_msg)
    #     self.assertEqual(False, bq.charge())

    # def test_incorrect_charge_voltage_on_tick(self):
    #     pack = self.controller.pack
    #     cells = self.controller.cells
    #     bq = self.controller.bq
    #     bq.charge(False)
    #
    #     self.state.enter()
    #     self.assertEqual(True, bq.charge())
    #
    #     pack.stub_pack_v = cells.max_serial_voltage() + 0.6
    #     self.state.tick()
    #     self.assertEqual("alert", self.sm.last_event)
    #     self.assertEqual("Wrong Charge V: 38.4", self.controller.alert_msg)

    # def count_log_type(self, type):
    #     count = 0
    #     for line in self.controller.logger.log:
    #         if line.startswith(type):
    #             count += 1
    #     return count
    #
    # def test_logs_pack_info_on_tick(self):
    #     self.state.tick()
    #     self.assertEqual(1, self.controller.logger.count_log_type("pack:"))
    #
    # def test_logs_cells_eveny_10_ticks(self):
    #     self.state.tick()
    #     self.assertEqual(1, self.controller.logger.count_log_type("cells:"))
    #
    # def test_logs_temps_eveny_10_ticks(self):
    #     self.state.tick()
    #     self.assertEqual(1, self.controller.logger.count_log_type("temps:"))
    #
    # def test_monitors_pack_info_on_tick(self):
    #     self.state.tick()
    #     self.assertEqual(1, self.controller.serial.count_log_type("pack:"))
    #
    # def test_serials_cells_eveny_10_ticks(self):
    #     self.state.tick()
    #     self.assertEqual(1, self.controller.serial.count_log_type("cells:"))
    #
    # def test_serials_temps_eveny_10_ticks(self):
    #     self.state.tick()
    #     self.assertEqual(1, self.controller.serial.count_log_type("temps:"))

    def test_over_temp_alert(self):
        temps = self.controller.temps
        self.state.enter()

        temps.stub_temp1 = self.conf.TEMP_MAX_PACK_CHG + 1
        self.state.tick()

        self.assertEqual("alert", self.sm.last_event)
        self.assertEqual("Charge Over-Temp", self.controller.alert_msg)

    def test_under_temp_alert(self):
        temps = self.controller.temps
        self.state.enter()

        temps.stub_temp1 = self.conf.TEMP_MIN_PACK_CHG - 1
        self.state.tick()

        self.assertEqual("alert", self.sm.last_event)
        self.assertEqual("Charge Under-Temp", self.controller.alert_msg)





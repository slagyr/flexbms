import unittest

from bms.bq import CC_ONESHOT
from bms.conf import CONF
from bms.states.normal import NormalState
from test.states.mock_machine import MockStatemachine


class NormalStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.controller.logger.setup()
        self.state = NormalState(self.sm)

    def test_entry_turns_stuff_on(self):
        bq = self.controller.bq
        driver = self.controller.driver
        bq.discharge(False)
        bq.charge(False)
        bq.adc(False)
        driver.chargepump(False)
        driver.precharge(True)

        self.state.enter()

        self.assertEqual(True, bq.discharge())
        self.assertEqual(False, bq.charge())
        self.assertEqual(False, bq.adc())
        self.assertEqual(True, bq.get_reg_bit(CC_ONESHOT))
        self.assertEqual(True, driver.chargepump())
        self.assertEqual(False, driver.precharge())

    def test_sets_tick_interval(self):
        self.state.enter()
        self.assertEqual(500, self.controller.sm_tick_interval())

    def test_entry_sets_home_screen_to_bargraph(self):
        self.state.enter()
        self.assertEqual(self.controller.bargraph_screen, self.controller.home_screen)

    def test_charge_FET_closes_when_current_detected(self):
        pack = self.controller.pack
        bq = self.controller.bq
        pack.stub_amps_in = 0
        self.state.enter()

        self.state.tick()
        self.assertEqual(False, bq.charge())

        pack.stub_amps_in = -0.05  # under threshold
        self.state.tick()
        self.assertEqual(False, bq.charge())

        pack.stub_amps_in = -0.2  # surpasses threshold
        self.state.tick()
        self.assertEqual(True, bq.charge())

    def test_charge_FET_opens_when_current_dies(self):
        bq = self.controller.bq
        pack = self.controller.pack
        self.state.enter()

        pack.stub_amps_in = -5  # make sure FET is one
        self.state.tick()
        self.assertEqual(True, bq.charge())

        pack.stub_amps_in = 0  # current goes away
        self.state.tick()
        self.assertEqual(False, bq.charge())
        
    def test_voltage_loaded_every_10_ticks(self):
        bq = self.controller.bq

        self.state.enter()
        self.assertEqual(False, bq.voltages_loaded)
        self.assertEqual(False, bq.adc())

        for i in range(8):
            self.state.tick()
        self.assertEqual(False, bq.voltages_loaded)
        self.assertEqual(False, bq.adc())

        self.state.tick() # 9th tick : turn on ADC
        self.assertEqual(False, bq.voltages_loaded)
        self.assertEqual(True, bq.adc())
        self.assertEqual(9, self.state.counter)

        self.state.tick() # 10th tick : load voltage, turn off ADC
        self.assertEqual(True, bq.voltages_loaded)
        self.assertEqual(False, bq.adc())
        self.assertEqual(0, self.state.counter)

    def test_low_V_triggers_event(self):
        self.state.enter()
        self.controller.cells[5].voltage = 1.1

        for i in range(10):
            self.state.tick()
        self.assertEqual("low_v", self.sm.last_event)

    def test_pow_on_event_when_charger_detected(self):
        driver = self.controller.driver
        cells = self.controller.cells
        bq = self.controller.bq
        bq.stub_batt_v = 30.0

        self.state.enter()
        self.state.tick()
        self.assertEqual(None, self.sm.last_event)

        self.controller.pack.expire()
        driver.stub_pack_v = cells.max_serial_voltage()

        self.state.tick()
        self.assertEqual("pow_on", self.sm.last_event)

    def test_logs_pack_info_on_tick(self):
        self.state.tick()
        self.assertEqual(1, self.controller.logger.count_log_type("pack:"))

    def test_logs_cells_eveny_10_ticks(self):
        for i in range(10):
            self.state.tick()
        self.assertEqual(1, self.controller.logger.count_log_type("cells:"))

    def test_logs_temps_eveny_10_ticks(self):
        for i in range(10):
            self.state.tick()
        self.assertEqual(1, self.controller.logger.count_log_type("temps:"))

    def test_over_temp_alert(self):
        temps = self.controller.temps
        self.state.enter()

        temps.stub_temp1 = CONF.TEMP_MAX_PACK_DSG + 1
        for i in range(10):
            self.state.tick()

        self.assertEqual("alert", self.sm.last_event)
        self.assertEqual("Discharge Over-Temp", self.controller.alert_msg)

    def test_under_temp_alert(self):
        temps = self.controller.temps
        self.state.enter()

        temps.stub_temp1 = CONF.TEMP_MIN_PACK_DSG - 1
        for i in range(10):
            self.state.tick()

        self.assertEqual("alert", self.sm.last_event)
        self.assertEqual("Discharge Under-Temp", self.controller.alert_msg)

    def test_discharge_overcurrent(self):
        pack = self.controller.pack

        pack.stub_amps_in = CONF.CELL_PARALLEL * CONF.CELL_MAX_DSG_I + CONF.PACK_I_TOLERANCE + 0.1
        self.state.tick()

        self.assertEqual("alert", self.sm.last_event)
        self.assertEqual("Discharge Overcurrent", self.controller.alert_msg)

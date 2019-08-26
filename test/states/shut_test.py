import unittest

from bms.states.shut import ShutState
from test.states.mock_machine import MockStatemachine


class ShutStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.controller.setup()
        self.state = ShutState(self.sm)

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
        self.assertEqual(400, self.controller.sm_tick_interval())

    def test_check_voltage_once_every_n_ticks(self):
        bq = self.controller.bq
        self.state.enter()

        self.state.tick()
        self.assertEqual(False, bq.voltages_loaded)
        self.assertEqual(True, self.state.in_wake_cycle)
        self.assertEqual(True, bq.adc())
        self.assertEqual(100, self.controller.sm_tick_interval())

        self.state.tick()
        self.assertEqual(True, bq.voltages_loaded)
        self.assertEqual(False, self.state.in_wake_cycle)
        self.assertEqual(False, bq.adc())
        self.assertEqual(400, self.controller.sm_tick_interval())

import unittest

from bms.states.empty import EmptyState
from test.states.mock_machine import MockStatemachine


class EmptyStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
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
        self.assertEqual(600000, self.controller.sm_tick_interval())

    def test_entry_sets_home_screen_to_low_v(self):
        self.state.enter()

        self.assertEqual(self.controller.low_v_screen, self.controller.home_screen)
        
    def test_tick_wakes_to_check_voltage(self):
        bq = self.controller.bq
        self.state.enter()
        self.controller.screen_outdated(False)

        self.state.tick()
        self.assertEqual(False, bq.voltages_loaded)
        self.assertEqual(True, self.state.in_wake_cycle)
        self.assertEqual(True, bq.adc())
        self.assertEqual(500, self.controller.sm_tick_interval())
        self.assertEqual(False, self.controller.screen_outdated())

        self.state.tick()
        self.assertEqual(True, bq.voltages_loaded)
        self.assertEqual(False, self.state.in_wake_cycle)
        self.assertEqual(False, bq.adc())
        self.assertEqual(600000, self.controller.sm_tick_interval())
        self.assertEqual(True, self.controller.screen_outdated())


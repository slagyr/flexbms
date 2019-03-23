import unittest

from bms.states.alert import AlertState
from test.states.mock_machine import MockStatemachine


class AlertStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.state = AlertState(self.sm)

    def test_entry_turns_stuff_on(self):
        bq = self.controller.bq
        driver = self.controller.driver
        bq.discharge(True)
        bq.charge(True)
        bq.adc(True)
        driver.chargepump(True)
        driver.precharge(True)

        self.state.enter()

        self.assertEqual(False, bq.discharge())
        self.assertEqual(False, bq.charge())
        self.assertEqual(False, bq.adc())
        self.assertEqual(False, driver.chargepump())
        self.assertEqual(False, driver.precharge())

    def test_sets_tick_interval(self):
        self.state.enter()
        self.assertEqual(10000, self.controller.sm_tick_interval())

    def test_entry_sets_home_screen_to_alertscreen(self):
        self.state.enter()
        self.assertEqual(self.controller.alert_screen, self.controller.home_screen)

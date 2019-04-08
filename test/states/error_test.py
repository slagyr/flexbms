import unittest

from bms.states.error import ErrorState
from test.states.mock_machine import MockStatemachine


class ErrorStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.state = ErrorState(self.sm)

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
        self.assertEqual(3600000, self.controller.sm_tick_interval())

    def test_entry_sets_home_screen_to_alertscreen(self):
        self.state.enter()
        self.assertEqual(self.controller.error_screen, self.controller.home_screen)
        self.assertEqual(self.controller.error_screen, self.controller.screen)





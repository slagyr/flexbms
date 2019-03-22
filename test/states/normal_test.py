import unittest

from bms.states.normal import NormalState
from test.states.mock_machine import MockStatemachine


class NormalStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.state = NormalState(self.sm)

    def test_entry_turns_stuff_on(self):
        bq = self.controller.bq
        driver = self.controller.driver
        bq.discharge(False)
        bq.charge(False)
        bq.adc(False)
        # bq.cc(True)
        driver.chargepump(False)
        driver.precharge(True)

        self.state.enter()

        self.assertEqual(True, bq.discharge())
        self.assertEqual(False, bq.charge())
        # self.assertEqual(False, bq.adc())
        # self.assertEqual(False, bq.cc())
        self.assertEqual(True, driver.chargepump())
        self.assertEqual(False, driver.precharge())

    def test_sets_tick_interval(self):
        self.state.enter()
        self.assertEqual(500, self.controller.sm_tick_interval())

    def test_entry_sets_home_screen_to_bargraph(self):
        self.state.enter()
        self.assertEqual(self.controller.bargraph_screen, self.controller.home_screen)


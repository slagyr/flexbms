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


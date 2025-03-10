import unittest

from bms.states.alert import AlertState
from test.states.mock_machine import MockStatemachine


class AlertStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.controller.setup()
        self.state = AlertState(self.sm)

    def test_entry_turns_stuff_off(self):
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

    def test_exit_clears_alert(self):
        self.controller.alert_msg = "fooey"
        self.controller.bq.faults = [1, 2, 3]
        self.state.enter()

        self.state.exit()

        self.assertEqual(True, self.controller.bq.was_sys_stat_cleared)
        self.assertEqual(None, self.controller.alert_msg)

    def test_enter_logs_alert(self):
        logger = self.controller.logger
        bq = self.controller.bq
        bq.faults = [1]
        self.controller.alert_msg = "blah"

        self.state.enter()

        self.assertEqual("alert: blah, Discharge Overcurrent\n", logger.log[-1])

    def test_enter_serializes_alert(self):
        serial = self.controller.serial
        bq = self.controller.bq
        bq.faults = [1]
        self.controller.alert_msg = "blah"

        self.state.enter()

        self.assertEqual("alert: blah, Discharge Overcurrent\n", serial.out[-1])



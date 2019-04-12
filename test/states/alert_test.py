import unittest

from bms.states.alert import AlertState
from test.states.mock_machine import MockStatemachine


class AlertStateTest(unittest.TestCase):

    def setUp(self):
        self.sm = MockStatemachine()
        self.controller = self.sm.controller
        self.controller.setup()
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
        self.assertEqual(self.controller.alert_screen, self.controller.screen)

    # def test_max_charge_current_exceeded_alert(self):
    #
    #     self.assertEqual(1, 2)

    def test_logs_pack_info_on_tick(self):
        self.state.tick()
        self.assertEqual(1, len(self.controller.logger.pack_log))

    def test_logs_cells_on_tick(self):
        self.state.tick()
        self.assertEqual(1, len(self.controller.logger.cell_log))

    def test_logs_temps_on_tick(self):
        self.state.tick()
        self.assertEqual(1, len(self.controller.logger.temp_log))

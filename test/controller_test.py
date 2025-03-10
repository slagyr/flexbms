import unittest
import bms.conf as conf
from bms import util
from bms.bq import OV
from bms.controller import Controller
from bms.pack import Pack
from bms.temps import Temps
from test.mock_cells import MockCells
from test.mock_bq import MockBQ
from test.mock_clock import MockClock
from test.mock_conf import MockConfig
from test.mock_driver import MockDriver
from test.mock_logger import MockLogger
from test.mock_serial import MockSerial
from test.states.mock_machine import MockStatemachine
from test.states.mock_state import MockState

class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.logger = MockLogger()
        self.serial = MockSerial()
        self.conf = MockConfig()
        self.bq = MockBQ(self.conf)
        self.driver = MockDriver()
        self.cells = MockCells(self.conf, self.bq, 9)
        self.temps = Temps(self.bq)
        self.pack = Pack(self.bq, self.driver)

        self.clock = MockClock()
        util.clock = self.clock

        self.controller = Controller(self.conf, util.clock)
        self.controller.logger = self.logger
        self.controller.serial = self.serial
        self.controller.bq = self.bq
        self.controller.driver = self.driver
        self.controller.cells = self.cells
        self.controller.temps = self.temps
        self.controller.pack = self.pack

        self.controller.setup()

    def test_setup(self):
        self.assertEqual(True, self.bq.was_setup)
        self.assertEqual(True, self.cells.was_setup)
        self.assertEqual(True, self.driver.was_setup)

    def test_updates_balancing_when_disabled(self):
        conf.BALANCE_ENABLED = False
        self.assertFalse(self.cells.was_balancing_updated)
        self.controller.tick()
        self.assertFalse(self.cells.was_balancing_updated)

    def test_has_statemachine(self):
        self.assertIsNotNone(self.controller.sm)
        self.assertEqual(self.controller, self.controller.sm.controller)

    def test_statemachine_get_setup(self):
        self.controller.setup()
        self.assertTrue(len(self.controller.sm.trans) > 0)

    def test_sm_tick_interval(self):
        self.assertEqual(500, self.controller.sm_tick_interval())
        self.controller.sm_tick_interval(1000)
        self.assertEqual(1000, self.controller.sm_tick_interval())

    def test_sm_ticks_at_assigned_interval(self):
        state = MockState()
        self.controller.sm.state = state
        self.clock.mils = 2000
        self.controller.sm_tick_interval(1234)

        self.assertEqual(0, state.tick_count)
        self.controller.tick()
        self.assertEqual(1, state.tick_count)

        self.clock.mils = 3222
        self.controller.tick()
        self.assertEqual(1, state.tick_count)

        self.clock.mils = 3235
        self.controller.tick()
        self.assertEqual(2, state.tick_count)

    def test_handle_alert(self):
        self.assertEqual(False, self.controller._has_alert)
        self.controller.handle_alert()
        self.assertEqual(True, self.controller._has_alert)

    def test_tick_processes_alerts(self):
        sm = MockStatemachine()
        self.controller.sm = sm

        self.controller.tick()
        self.assertEqual(False, self.bq.alert_processed)

        self.bq.faults = []
        self.controller.handle_alert()
        self.controller.tick()
        self.assertEqual(True, self.bq.alert_processed)
        self.assertEqual(None, sm.last_event)

        self.bq.faults = ["Yup"]
        self.controller.handle_alert()
        self.controller.tick()
        self.assertEqual(True, self.bq.alert_processed)
        self.assertEqual("alert", sm.last_event)


    def test_tick_handled_undervoltage_in_prechg_state(self):
        sm = MockStatemachine()
        self.controller.sm = sm
        sm.state = sm._prechg

        self.bq.faults = [OV]
        self.controller.handle_alert()
        self.controller.tick()
        self.assertEqual(True, self.bq.alert_processed)
        self.assertEqual(None, sm.last_event)

    def test_logger(self):
        self.controller.setup()

        self.assertEqual(True, self.logger.was_setup)

    def test_caches_expire_after_tick(self):
        self.cells.loaded = True
        self.temps.loaded = True
        self.pack.loaded = True

        self.controller.tick()

        self.assertEqual(False, self.cells.loaded)
        self.assertEqual(False, self.temps.loaded)
        self.assertEqual(False, self.pack.loaded)

    def test_logs_tick(self):
        self.controller.tick()
        self.assertEqual(1, self.logger.count_log_type("tick:"))
        self.controller.tick()
        self.assertEqual(2, self.logger.count_log_type("tick:"))













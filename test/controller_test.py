import unittest
import bms.conf as conf
from bms import util
from bms.controller import Controller
from bms.pack import Pack
from bms.screens.bargraph import BargraphScreen
from bms.screens.splash import SplashScreen
from bms.temps import Temps
from test.mock_cells import MockCells
from test.mock_bq import MockBQ
from test.mock_clock import MockClock
from test.mock_display import MockDisplay
from test.mock_driver import MockDriver
from test.mock_logger import MockLogger
from test.mock_rebooter import MockRebooter
from test.mock_rotary import MockRotary
from test.screens.mock_screen import MockScreen
from test.states.mock_machine import MockStatemachine
from test.states.mock_state import MockState

class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.logger = MockLogger()
        self.display = MockDisplay()
        self.bq = MockBQ()
        self.rotary = MockRotary()
        self.driver = MockDriver()
        self.cells = MockCells(self.bq, 9)
        self.temps = Temps(self.bq)
        self.pack = Pack(self.bq, self.driver)

        self.clock = MockClock()
        util.clock = self.clock

        self.controller = Controller(util.clock)
        self.controller.logger = self.logger
        self.controller.display = self.display
        self.controller.bq = self.bq
        self.controller.rotary = self.rotary
        self.controller.driver = self.driver
        self.controller.cells = self.cells
        self.controller.temps = self.temps
        self.controller.pack = self.pack

        self.controller.setup()

    def test_properties(self):
        self.assertIsNotNone(self.controller.display)

    def test_screens(self):
        self.assertIsNotNone(self.controller.bargraph_screen)
        self.assertIsNotNone(self.controller.main_menu)
        self.assertIsNotNone(self.controller.splash_screen)
        self.assertIsNotNone(self.controller.error_screen)
        self.assertIsNotNone(self.controller.voltages_screen)

    def test_initial_home_screen(self):
        self.assertEqual(self.controller.bargraph_screen, self.controller.home_screen)
        
    def test_setting_home_screen_when_current_screen_is_not_home(self):
        self.controller.set_screen(self.controller.splash_screen)
        self.controller.set_home_screen(self.controller.voltages_screen)
        self.assertEqual(self.controller.voltages_screen, self.controller.home_screen)
        self.assertEqual(self.controller.splash_screen, self.controller.screen)

    def test_setting_home_screen_when_current_screen_IS_home(self):
        self.controller.set_screen(self.controller.home_screen)
        self.controller.set_home_screen(self.controller.voltages_screen)
        self.assertEqual(self.controller.voltages_screen, self.controller.home_screen)
        self.assertEqual(self.controller.voltages_screen, self.controller.screen)

    def test_setup(self):
        self.assertEqual(True, self.display.was_setup)
        self.assertEqual(True, self.bq.was_setup)
        self.assertEqual(True, self.cells.was_setup)
        self.assertEqual(True, self.rotary.was_setup)
        self.assertEqual(True, self.driver.was_setup)

    def test_splash_is_initial_screen(self):
        self.assertIsInstance(self.controller.screen, SplashScreen)
        self.assertIs(self.controller.splash_screen, self.controller.screen)

    def test_screen_timeout(self):
        self.controller.tick()
        self.clock.mils = 4000
        self.controller.tick()
        self.assertIsInstance(self.controller.screen, BargraphScreen)
        # self.controller.display.print_buffer()
        self.assertIs(self.controller.home_screen, self.controller.screen)
        self.assertEqual(4000, self.controller.last_user_event_time)

    def test_screen_updated_on_tick(self):
        screen = self.controller.screen = MockScreen()
        self.controller.tick()
        self.assertEqual(True, screen.was_updated)

        screen.was_updated = False
        self.controller.screen_outdated(True)
        self.controller.tick()
        self.assertEqual(True, screen.was_updated)

    def test_updates_balancing_when_disabled(self):
        conf.BALANCE_ENABLED = False
        self.assertFalse(self.cells.was_balancing_updated)
        self.controller.tick()
        self.assertFalse(self.cells.was_balancing_updated)
        
    def test_rotary_gets_rested(self):
        self.rotary.clicked = True
        self.controller.tick()
        self.assertEqual(True, self.rotary.was_rested)
        
    def test_rotary_updates_reset_last_user_event(self):
        self.rotary.clicked = True
        self.clock.mils = 100
        self.controller.tick()
        self.assertEqual(100, self.controller.last_user_event_time)
        self.assertEqual(self.controller.splash_screen, self.controller.screen)

    def test_has_statemachine(self):
        self.assertIsNotNone(self.controller.sm)
        self.assertEqual(self.controller, self.controller.sm.controller)

    def test_statemachine_get_setup(self):
        self.controller.setup()
        self.assertTrue(len(self.controller.sm.trans) > 0)

    def test_screen_updated_when_needed(self):
        screen = MockScreen()
        self.controller.set_screen(screen)
        self.controller.screen_outdated(True)
        self.controller.tick()
        self.assertEqual(False, self.controller.screen_outdated())
        self.assertEqual(True, screen.was_updated)

    def test_screen_not_updated_when_not_needed(self):
        screen = MockScreen()
        self.controller.set_screen(screen)
        screen.was_updated = False
        self.controller.screen_outdated(False)
        self.controller.tick()
        self.assertEqual(False, self.controller.screen_outdated())
        self.assertEqual(False, screen.was_updated)

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

    def test_controller_has_reboot_menu_item(self):
        menu = self.controller.main_menu
        last = menu.items[-1]

        self.assertEqual("Reboot", last.menu_name())

    def test_reboot_menu_item_reboots(self):
        rebooter = MockRebooter()
        self.controller.rebooter = rebooter
        menu = self.controller.main_menu
        last = menu.items[-1]

        last.menu_sel()
        
        self.assertEqual(True, rebooter.was_rebooted)












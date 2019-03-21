import unittest
import bms.conf as conf
from bms import util
from bms.controller import Controller
from bms.screens.bargraph import BargraphScreen
from bms.screens.splash import SplashScreen
from test.mock_cells import MockCells
from test.mock_bq import MockBQ
from test.mock_clock import MockClock
from test.mock_display import MockDisplay
from test.mock_driver import MockDriver
from test.mock_rotary import MockRotary
from test.screens.mock_screen import MockScreen
from test.states.mock_state import MockState


class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.display = MockDisplay()
        self.bq = MockBQ()
        self.cells = MockCells(9)
        self.rotary = MockRotary()
        self.driver = MockDriver()

        self.clock = MockClock()
        util.clock = self.clock

        self.controller = Controller(util.clock)
        self.controller.display = self.display
        self.controller.bq = self.bq
        self.controller.cells = self.cells
        self.controller.rotary = self.rotary
        self.controller.driver = self.driver

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
        self.controller.tick()
        self.assertEqual(True, screen.was_updated)
        
    def test_updates_cells_on_tick(self):
        self.assertFalse(self.bq.voltages_loaded)
        self.controller.tick()
        self.assertTrue(self.bq.voltages_loaded)

    def test_updates_balancing(self):
        self.assertFalse(self.cells.balancing_updated)
        self.controller.tick()
        self.assertTrue(self.cells.balancing_updated)

    def test_updates_balancing_when_disabled(self):
        conf.BALANCE_ENABLED = False
        self.assertFalse(self.cells.balancing_updated)
        self.controller.tick()
        self.assertFalse(self.cells.balancing_updated)
        
    # def test_balancing_only_updates_by_interval(self):
    #     conf.BALANCE_ENABLED = True
    #     conf.BALANCE_INTERVAL = 60
    #     self.controller.tick(0)
    #     self.assertEqual(True, self.cells.balancing_updated)
    #
    #     self.cells.balancing_updated = False
    #     self.controller.tick(1)
    #     self.assertEqual(False, self.cells.balancing_updated)
    #     self.controller.tick(2)
    #     self.assertEqual(False, self.cells.balancing_updated)
    #
    #     self.controller.tick(61)
    #     self.assertEqual(True, self.cells.balancing_updated)
        
    def test_rotary_gets_rested(self):
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

    def test_statemachine_gets_ticks(self):
        state = MockState()
        self.assertEqual(0, state.tick_count)

        self.controller.sm.state = state
        self.controller.tick()

        self.assertEqual(1, state.tick_count)





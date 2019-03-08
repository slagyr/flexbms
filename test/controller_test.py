import unittest
from bms.controller import Controller
from bms.screens.home import HomeScreen
from bms.screens.splash import SplashScreen
from test.mock_cells import MockCells
from test.mock_bq import MockBQ
from test.mock_display import MockDisplay
from test.screens.mock_screen import MockScreen

class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.display = MockDisplay()
        self.bq = MockBQ()
        self.cells = MockCells(self.bq, 9)

        self.controller = Controller()
        self.controller.display = self.display
        # self.controller.display = Display(MockI2C())
        self.controller.bq = self.bq
        self.controller.cells = self.cells

        self.controller.setup()

    def test_properties(self):
        self.assertIsNotNone(self.controller.display)

    def test_setup(self):
        self.assertEqual(True, self.display.was_setup)
        self.assertEqual(True, self.bq.was_setup)
        self.assertEqual(True, self.cells.was_setup)

    def test_splash_is_initial_screen(self):
        self.assertIsInstance(self.controller.screen, SplashScreen)
        self.assertIs(self.controller.splash_screen, self.controller.screen)

    def test_screen_timeout(self):
        self.controller.tick(0)
        self.controller.tick(4)
        self.assertIsInstance(self.controller.screen, HomeScreen)
        # self.controller.display.print_buffer()
        self.assertIs(self.controller.home_screen, self.controller.screen)
        self.assertEqual(4, self.controller.last_user_event_time)

    def test_screen_updated_on_tick(self):
        screen = self.controller.screen = MockScreen()
        self.controller.tick(0)
        self.assertEqual(True, screen.was_updated)

        screen.was_updated = False
        self.controller.tick(1)
        self.assertEqual(True, screen.was_updated)
        
    def test_updates_cells_on_tick(self):
        self.assertFalse(self.cells.was_updated)
        self.controller.tick(0)
        self.assertTrue(self.cells.was_updated)



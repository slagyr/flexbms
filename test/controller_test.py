import unittest
from bms.controller import Controller
from bms.bq76940 import BQ76940
from test.mock_bq_i2c import MockBqI2C
from test.mock_display import MockDisplay
from bms.screens.home import HomeScreen
from bms.screens.splash import SplashScreen


class MockBq(BQ76940):

    def __init__(self):
        i2c = MockBqI2C()
        super().__init__(i2c)
        self.was_setup = False

    def setup(self):
        self.was_setup = True


class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.display = MockDisplay()
        self.bq = MockBq()

        self.controller = Controller()
        self.controller.display = self.display
        # self.controller.display = Display(MockI2C())
        self.controller.bq = self.bq

        self.controller.setup()

    def test_properties(self):
        self.assertIsNotNone(self.controller.display)

    def test_setup(self):
        self.assertEqual(True, self.controller.display.was_setup)
        self.assertEqual(True, self.controller.bq.was_setup)

    def test_splash_is_initial_screen(self):
        self.assertIsInstance(self.controller.screen, SplashScreen)
        self.assertIs(self.controller.splash_screen, self.controller.screen)

    def test_screen_timeout(self):
        self.controller.tick(0)
        self.controller.tick(3.1)
        self.assertIsInstance(self.controller.screen, HomeScreen)
        # self.controller.display.print_buffer()
        self.assertIs(self.controller.home_screen, self.controller.screen)
        self.assertEqual(3.1, self.controller.last_user_event_time)


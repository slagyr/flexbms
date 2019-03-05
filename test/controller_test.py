import unittest
from bms.controller import Controller
from test.mock_i2c import MockI2C
from bms.ssd1306.display import Display
from test.mock_display import MockDisplay
from bms.screens.home import HomeScreen
from bms.screens.splash import SplashScreen


class ControllerTest(unittest.TestCase):

    def setUp(self):
        self.controller = Controller()
        self.controller.display = MockDisplay()
        # self.controller.display = Display(MockI2C())
        self.controller.setup()

    def test_properties(self):
        self.assertIsNotNone(self.controller.display)

    def test_setup(self):
        self.assertEqual(True, self.controller.display.was_setup)

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


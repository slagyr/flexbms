import unittest
import bms.bin
from mock_controller import MockController
from screens.splash import SplashScreen


class SplashScreenTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.screen = SplashScreen(self.controller)

    def test_init(self):
        self.assertEqual(self.controller, self.screen.controller)

    def test_enter_loads_splash(self):
        self.screen.enter()
        byxels = bms.bin.load("splash")

        self.assertEqual(byxels, self.controller.display.drawings[0][4])
        self.assertEqual(True, self.controller.display.was_shown)

    def test_timeout(self):
        self.assertEqual(3, self.screen.idle_timeout)


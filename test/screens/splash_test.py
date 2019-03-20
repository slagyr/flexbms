import unittest
from bms.util import load_binary
from test.mock_controller import MockController
from bms.screens.splash import SplashScreen


class SplashScreenTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.screen = SplashScreen(self.controller)

    def test_init(self):
        self.assertEqual(self.controller, self.screen.controller)

    def test_enter_loads_splash(self):
        self.screen.enter()
        byxels = load_binary("splash")

        self.assertEqual(byxels[:500], self.controller.display.buffer[:500])
        self.assertEqual(True, self.controller.display.was_shown)

    def test_timeout(self):
        self.assertEqual(3000, self.screen.idle_timeout)


from bms.screens.splash import SplashScreen
from test.mock import Mock


class MockScreen(Mock):
    def __init__(self):
        self.was_entered = False
        self.was_updated = False
        self.controller = "Controller"
        self.idle_timeout = 42
        self.assert_mock(SplashScreen("controller"))

    def enter(self):
        self.was_entered = True

    def update(self):
        self.was_updated = True
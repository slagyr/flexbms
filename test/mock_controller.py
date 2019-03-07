from bms.controller import Controller
from test.mock import Mock
from test.mock_display import MockDisplay


class MockController(Mock):

    last_user_event_time = 0
    splash_screen = "splash"
    home_screen = "home"

    def __init__(self):
        self.display = MockDisplay()
        self.screen = None
        self.cells = "cells"
        self.bq = "bq"
        self.assert_mock(Controller())

    def setup(self):
        pass

    def tick(self):
        pass

    def set_screen(self):
        pass


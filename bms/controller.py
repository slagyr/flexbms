from bms.screens.home import HomeScreen
from bms.screens.splash import SplashScreen
import time


class Controller:
    def __init__(self):
        self.display = None
        self.screen = None
        self.last_user_event_time = time.monotonic()
        self.splash_screen = SplashScreen(self)
        self.home_screen = HomeScreen(self)

    def setup(self):
        self.display.setup()

        self.set_screen(self.splash_screen)

    def set_screen(self, screen):
        self.screen = screen
        self.screen.enter()

    def tick(self, secs):

        print("secs: " + str(secs))

        if secs > self.last_user_event_time + self.screen.idle_timeout:
            self.set_screen(self.home_screen)
            self.last_user_event_time = secs
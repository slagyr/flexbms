import time
import bms.conf as conf
from bms.screens.home import HomeScreen
from bms.screens.splash import SplashScreen
from bms.util import clocked_fn


class Controller:
    def __init__(self):
        self.display = None
        self.bq = None
        self.cells = None
        self.screen = None
        self.rotary = None
        self.events = None

        self.last_user_event_time = time.monotonic()
        self.splash_screen = SplashScreen(self)
        self.home_screen = HomeScreen(self)

        self.next_balance_time = -1

    def setup(self):
        self.display.setup()
        self.set_screen(self.splash_screen)

        self.bq.setup()
        self.cells.setup()

    def set_screen(self, screen):
        self.screen = screen
        self.screen.enter()

    @clocked_fn
    def tick(self, secs):
        self.events.dispatch()
        self.bq.load_cell_voltages(self.cells)

        # for cell in self.cells:
        #     print("cell " + str(cell.index) + ": " + str(cell.voltage))

        if conf.BALANCE_ENABLED and secs > self.next_balance_time:
            self.cells.update_balancing(self.bq)
            self.next_balance_time = secs + conf.BALANCE_INTERVAL

        if secs > self.last_user_event_time + self.screen.idle_timeout:
            self.set_screen(self.home_screen)
            self.last_user_event_time = secs

        self.screen.update()
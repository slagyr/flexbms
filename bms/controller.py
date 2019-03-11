import time
import bms.conf as conf
from bms.screens.home import HomeScreen
from bms.screens.menu import Menu
from bms.screens.splash import SplashScreen
from bms.screens.voltages import VoltagesScreen

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
        self.voltages_screen = VoltagesScreen(self)
        self.main_menu = Menu(self, "MAIN")

        self.next_balance_time = -1
        self.in_balance_rest = True

    def wire_menus(self):
        main = self.main_menu
        main.add(self.home_screen)
        main.add(self.voltages_screen)
        main.add(self.splash_screen)

    def setup(self):
        self.display.setup()
        self.set_screen(self.splash_screen)

        self.bq.setup()
        self.cells.setup()
        self.events.setup()
        self.rotary.setup()

        self.wire_menus()

    def set_screen(self, screen):
        self.screen = screen
        self.screen.enter()

    @clocked_fn
    def tick(self, secs):
        self.events.dispatch()
        self.bq.load_cell_voltages(self.cells)

        # for cell in self.cells:
        #     print("cell " + str(cell.index) + ": " + str(cell.voltage))

        self.balance(secs)

        if self.rotary.has_update():
            self.last_user_event_time = secs
        elif secs > self.last_user_event_time + self.screen.idle_timeout:
            self.set_screen(self.home_screen)
            self.last_user_event_time = secs

        self.screen.update()
        self.rotary.rest()

    def balance(self, secs):
        if conf.BALANCE_ENABLED and secs > self.next_balance_time:
            if self.in_balance_rest:
                self.in_balance_rest = False
                self.cells.update_balancing(self.bq)
                self.next_balance_time = secs + 60
            else:
                self.in_balance_rest = True
                self.cells.reset_balancing(self.bq)
                self.next_balance_time = secs + 3

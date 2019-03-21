import bms.conf as conf
from bms.screens.error import ErrorScreen
from bms.screens.bargraph import BargraphScreen
from bms.screens.menu import Menu
from bms.screens.splash import SplashScreen
from bms.screens.voltages import VoltagesScreen
from bms.states.machine import Statemachine

from bms.util import clocked_fn


class Controller:
    def __init__(self, clock):
        self.clock = clock
        self.display = None
        self.bq = None
        self.driver = None
        self.cells = None
        self.screen = None
        self.rotary = None

        self.last_user_event_time = 0
        self.splash_screen = SplashScreen(self)
        self.bargraph_screen = BargraphScreen(self)
        self.voltages_screen = VoltagesScreen(self)
        self.main_menu = Menu(self, "MAIN")
        self.error_screen = ErrorScreen(self)
        self.home_screen = self.bargraph_screen

        self.sm = Statemachine(self)

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

        self.sm.setup()
        self.bq.setup()
        self.driver.setup()
        self.cells.setup()
        self.rotary.setup()
        self.wire_menus()

    def set_home_screen(self, screen):
        at_home = self.home_screen == self.screen
        self.home_screen = screen
        if at_home:
            self.set_screen(screen)

    def set_screen(self, screen):
        self.screen = screen
        self.screen.enter()

    @clocked_fn
    def tick(self):
        my = self

        my.sm.tick()
        my.bq.load_cell_voltages(my.cells)
        my.balance()

        millis = my.clock.millis()
        if my.rotary.has_update():
            my.last_user_event_time = millis
        elif my.screen.idle_timeout and my.clock.millis_since(my.last_user_event_time) > my.screen.idle_timeout:
            my.set_screen(my.home_screen)
            my.last_user_event_time = millis

        my.screen.update()
        my.rotary.rest()

    def balance(self):
        millis = self.clock.millis()
        if conf.BALANCE_ENABLED and millis > self.next_balance_time:
            if self.in_balance_rest:
                self.in_balance_rest = False
                self.cells.update_balancing(self.bq)
                self.next_balance_time = self.clock.millis_after(millis, 60000)
            else:
                self.in_balance_rest = True
                self.cells.reset_balancing(self.bq)
                self.next_balance_time = self.clock.millis_after(millis, 3000)

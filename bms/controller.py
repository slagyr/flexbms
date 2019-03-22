import bms.conf as conf
from bms.screens.error import ErrorScreen
from bms.screens.bargraph import BargraphScreen
from bms.screens.low_v import LowVScreen
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
        self.low_v_screen = LowVScreen(self)

        self.home_screen = self.bargraph_screen

        self.sm = Statemachine(self)
        self._sm_tick_interval = 500
        self._last_sm_tick = 0
        self._screen_outdated = True
        self._has_alert = False

        self.next_balance_time = -1
        self.in_balance_rest = True

    def wire_menus(self):
        main = self.main_menu
        main.add(self.bargraph_screen)
        main.add(self.voltages_screen)
        main.add(self.splash_screen)
        main.add(self.low_v_screen)

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

    def sm_tick_interval(self, millis=None):
        if millis is None:
            return self._sm_tick_interval
        else:
            self._sm_tick_interval = millis

    def screen_outdated(self, outdated=None):
        if outdated is None:
            return self._screen_outdated
        else:
            self._screen_outdated = outdated

    def handle_alert(self):
        self._has_alert = True

    @clocked_fn
    def tick(self):
        my = self
        millis = my.clock.millis()

        if my._has_alert:
            my._has_alert = False
            my.bq.process_alert()
            if my.bq.faults:
                my.sm.alert()

        # my.bq.load_cell_voltages(my.cells)
        # my.balance()

        if my.rotary.has_update():
            my.last_user_event_time = millis
            my.screen.user_input()
            my.rotary.rest()
        else:
            idle_millis = my.clock.millis_diff(millis, my.last_user_event_time)
            if my.screen.idle_timeout and idle_millis >= my.screen.idle_timeout:
                my.set_screen(my.home_screen)
                my.last_user_event_time = millis

        tickless_millis = my.clock.millis_diff(millis, my._last_sm_tick)
        if tickless_millis >= my._sm_tick_interval:
            my.sm.tick()
            my._last_sm_tick = millis

        if my._screen_outdated:
            my.screen.update()
            my._screen_outdated = False

    def balance(self):
        millis = self.clock.millis()
        if conf.BALANCE_ENABLED and millis > self.next_balance_time:
            if self.in_balance_rest:
                self.in_balance_rest = False
                self.cells.update_balancing(self.bq)
                self.next_balance_time = self.clock.millis_add(millis, 60000)
            else:
                self.in_balance_rest = True
                self.cells.reset_balancing(self.bq)
                self.next_balance_time = self.clock.millis_add(millis, 3000)

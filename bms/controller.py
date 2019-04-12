from bms.screens.alert import AlertScreen
from bms.screens.charged import ChargedScreen
from bms.screens.dev import DevScreen
from bms.screens.error import ErrorScreen
from bms.screens.bargraph import BargraphScreen
from bms.screens.low_v import LowVScreen
from bms.screens.menu import Menu
from bms.screens.prechg import PrechargeScreen
from bms.screens.splash import SplashScreen
from bms.screens.voltages import VoltagesScreen
from bms.states.machine import Statemachine

from bms.util import clocked_fn

class HomeMenuItem:
    def __init__(self, controller):
        self.controller = controller

    def menu_name(self):
        return "Home Screen"

    def menu_sel(self):
        self.controller.set_screen(self.controller.home_screen)

class Controller:
    def __init__(self, clock):
        self.clock = clock
        self.logger = None
        self.display = None
        self.bq = None
        self.driver = None
        self.cells = None
        self.screen = None
        self.rotary = None
        self.temps = None
        self.pack = None

        self.last_user_event_time = 0
        self.splash_screen = SplashScreen(self)
        self.bargraph_screen = BargraphScreen(self)
        self.voltages_screen = VoltagesScreen(self)
        self.main_menu = Menu(self, "MAIN")
        self.error_screen = ErrorScreen(self)
        self.alert_screen = AlertScreen(self)
        self.low_v_screen = LowVScreen(self)
        self.charged_screen = ChargedScreen(self)
        self.prechg_screen = PrechargeScreen(self)
        self.dev_screen = DevScreen(self)

        self.home_screen = self.bargraph_screen

        self.sm = Statemachine(self)
        self._sm_tick_interval = 500
        self._last_sm_tick = 0
        self._screen_outdated = True
        self._has_alert = False
        self.alert_msg = None
        self.error_resume = False

    def wire_menus(self):
        main = self.main_menu
        main.add(HomeMenuItem(self))
        main.add(self.bargraph_screen)
        main.add(self.voltages_screen)
        main.add(self.dev_screen)
        main.add(self.splash_screen)

    def setup(self):
        self.logger.setup()
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

        my.cells.expire()
        my.temps.expire()
        my.pack.expire()

    def loaded_cells(self):
        my = self
        my.cells.load()
        my.logger.cells(my.cells)
        return my.cells

    def loaded_pack(self):
        my = self
        my.pack.load()
        my.logger.pack(my.pack)
        return my.pack

    def loaded_temps(self):
        my = self
        my.temps.load()
        my.logger.temps(my.temps)
        return my.temps

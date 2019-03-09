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

        self.last_user_event_time = time.monotonic()
        self.splash_screen = SplashScreen(self)
        self.home_screen = HomeScreen(self)

    def setup(self):
        self.display.setup()
        self.set_screen(self.splash_screen)
        # load splash screen first.  Let use be entertained while we do work.
        self.bq.setup()
        self.cells.setup()
        for id in range(1, 16):
            self.bq.set_balance_cell(id, False)


    def set_screen(self, screen):
        self.screen = screen
        self.screen.enter()

    @clocked_fn
    def tick(self, secs):

        self.bq.load_cell_voltages(self.cells)
        if conf.CELL_BALANCE_ENABLED:
            self.cells.update_balancing(self.bq)

        if secs > self.last_user_event_time + self.screen.idle_timeout:
            self.set_screen(self.home_screen)
            self.last_user_event_time = secs

        self.screen.update()

        cells_balancing = []
        for cell in self.cells:
            if cell.balancing:
                cells_balancing.append(cell.id)

        ids_balancing = []
        for id in range(1, 16):
            if self.bq.is_cell_balancing(id):
                ids_balancing.append(id)

        print("cells_balancing: " + str(cells_balancing))
        print("ids_balancing  : " + str(ids_balancing))
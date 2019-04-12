from bms.controller import Controller
from bms.pack import Pack
from bms.temps import Temps
from test.mock_bq import MockBQ
from test.mock_cells import MockCells
from test.mock_clock import MockClock
from test.mock_display import MockDisplay
from test.mock_driver import MockDriver
from test.mock_logger import MockLogger
from test.mock_rotary import MockRotary


class MockController(Controller):

    last_user_event_time = 0
    splash_screen = "splash"
    home_screen = "home"

    def __init__(self):
        super().__init__(MockClock())
        self.logger = MockLogger()
        self.display = MockDisplay()
        self.bq = MockBQ()
        self.rotary = MockRotary()
        self.driver = MockDriver()
        self.cells = MockCells(self.bq, 9)
        self.temps = Temps(self.bq)
        self.pack = Pack(self.bq, self.driver)



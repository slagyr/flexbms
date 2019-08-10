from bms.controller import Controller
from test.mock_bq import MockBQ
from test.mock_cells import MockCells
from test.mock_clock import MockClock
from test.mock_driver import MockDriver
from test.mock_logger import MockLogger
from test.mock_serial import MockSerial
from test.mock_pack import MockPack
from test.mock_temps import MockTemps


class MockController(Controller):

    last_user_event_time = 0
    splash_screen = "splash"
    home_screen = "home"

    def __init__(self):
        super().__init__(MockClock())
        self.logger = MockLogger()
        self.serial = MockSerial()
        self.bq = MockBQ()
        self.driver = MockDriver()
        self.cells = MockCells(self.bq, 9)
        self.temps = MockTemps(self.bq)
        self.pack = MockPack(self.bq, self.driver)



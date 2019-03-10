from bms.controller import Controller
from test.mock_bq import MockBQ
from test.mock_cells import MockCells
from test.mock_display import MockDisplay
from test.mock_rotary import MockRotary


class MockController(Controller):

    last_user_event_time = 0
    splash_screen = "splash"
    home_screen = "home"

    def __init__(self):
        super().__init__()
        self.display = MockDisplay()
        self.bq = MockBQ()
        self.cells = MockCells(9)
        self.rotary = MockRotary()



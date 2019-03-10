from bms.events import Events
from test.events_test import MockButtons


class MockEvents(Events):
    def __init__(self):
        super().__init__(MockButtons())
        self.dispatched = False

    def dispatch(self):
        self.dispatched = True
from bms.states.machine import Statemachine
from test.mock_controller import MockController


class MockStatemachine(Statemachine):

    def __init__(self):
        super().__init__(MockController())
        self.controller.sm = self
        self.last_event = None

    def handle_event(self, event):
        self.last_event = event
        super().handle_event(event)



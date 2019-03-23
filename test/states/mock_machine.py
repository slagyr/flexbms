from bms.states.machine import Statemachine
from test.mock_controller import MockController


class MockStatemachine(Statemachine):

    def __init__(self, controller=None):
        if controller:
            super().__init__(controller)
        else:
            super().__init__(MockController())
        self.controller.sm = self
        self.last_event = None

    def handle_event(self, event):
        self.last_event = event
        super().handle_event(event)



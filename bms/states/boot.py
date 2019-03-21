from bms.states.state import State


class BootState(State):
    def __init__(self, sm):
        super().__init__(sm)

    def tick(self, millis):
        self.sm.set_state(self.sm.eval)


from bms.states.state import State


class NormalState(State):
    def __init__(self, sm):
        super().__init__(sm)

    def tick(self, millis):
        pass

    def low_v(self):
        pass

    def pow_on(self):
        pass
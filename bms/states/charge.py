from bms.states.state import State


class ChargeState(State):
    def __init__(self, sm):
        super().__init__(sm)

    def tick(self, millis):
        pass

    def low_v(self):
        pass

    def pow_on(self):
        pass

    def pow_off(self):
        self.sm.set_state(self.sm.normal)


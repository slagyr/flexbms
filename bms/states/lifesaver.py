from bms.states.state import State


class LifeSaverState(State):
    def __init__(self, sm):
        super().__init__(sm)

    def tick(self, millis):
        pass

    def low_v(self):
        pass

    def pow_on(self):
        self.sm.set_state(self.sm.precharge)

    def norm_v(self):
        self.sm.set_state(self.sm.normal)



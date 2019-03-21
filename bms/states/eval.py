from bms.states.state import State


class EvalState(State):
    def __init__(self, sm):
        super().__init__(sm)

    def tick(self, millis):
        pass

    def low_v(self):
        self.sm.set_state(self.sm.lifesaver)

    def pow_on(self):
        self.sm.set_state(self.sm.charge)

    def norm_v(self):
        self.sm.set_state(self.sm.normal)




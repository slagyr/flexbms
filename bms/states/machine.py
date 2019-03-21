from bms.states.boot import BootState
from bms.states.charge import ChargeState
from bms.states.eval import EvalState
from bms.states.lifesaver import LifeSaverState
from bms.states.normal import NormalState
from bms.states.precharge import PrechargeState
from bms.util import log


class Statemachine:
    def __init__(self, context):
        self.context = context

        self.boot = BootState(self)
        self.eval = EvalState(self)
        self.lifesaver = LifeSaverState(self)
        self.precharge = PrechargeState(self)
        self.charge = ChargeState(self)
        self.normal = NormalState(self)

        self.state = self.boot

    def set_state(self, state):
        log("\tleaving: " + str(self.state))
        self.state.exit()
        log("\tentering: " + str(state))
        self.state = state
        self.state.enter()

    def tick(self, millis):
        log("SM event: tick")
        self.state.tick(millis)

    def low_v(self):
        log("SM event: low_v")
        self.state.low_v()

    def norm_v(self):
        log("SM event: norm_v")
        self.state.norm_v()

    def pow_on(self):
        log("SM event: pow_on")
        self.state.pow_on()

    def pow_off(self):
        log("SM event: pow_off")
        self.state.pow_off()


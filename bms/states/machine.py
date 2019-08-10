from bms.states.alert import AlertState
from bms.states.charge import ChargeState
from bms.states.error import ErrorState
from bms.states.eval import EvalState
from bms.states.empty import EmptyState
from bms.states.full import FullState
from bms.states.normal import NormalState
from bms.states.prechg import PreChgState


class Statemachine:
    def __init__(self, controller):
        self.controller = controller

        self._eval = EvalState(self)
        self._empty = EmptyState(self)
        self._prechg = PreChgState(self)
        self._charge = ChargeState(self)
        self._full = FullState(self)
        self._normal = NormalState(self)
        self._alert = AlertState(self)
        self._error = ErrorState(self)

        self.state = self._eval
        self.trans = {}

    def setup(self):
        with open('bms/states/sm.txt', "r") as f:
            lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 3 or len(parts) > 4:
                raise RuntimeError("Invalid statemachine transition: " + line)
            start = parts[0]
            event = parts[1]
            end = parts[2]
            action = parts[3] if len(parts) == 4 else None
            _end = getattr(self, "_" + end)
            _start = getattr(self, "_" + start) if start != "*" else "*"
            getattr(self, event) # just to make sure it exists
            _action = getattr(self.controller, action) if action else None
            self.trans[(_start, event)] = (_end, _action)

    def set_state(self, state):
        self.controller.log("\tleaving: " + self.state.__class__.__name__)
        if hasattr(self.state, "exit"):
            self.state.exit()
        self.controller.log("\tentering: " + state.__class__.__name__)
        self.controller.serial.state(state.__class__.__name__)
        self.state = state
        if hasattr(self.state, "enter"):
            self.state.enter()

    def handle_event(self, event):
        t = self.trans.get((self.state, event))
        if not t:
            t = self.trans.get(("*", event))
        if not t:
            self.controller.logger.error("Unimplemented transition!: " + str(self.__class__.__name__) + ":" + event)
        else:
            end = t[0]
            action = t[1]
            if action:
                action()
            self.set_state(end)

    def tick(self):
        self.state.tick()

    def low_v(self):
        self.controller.log("SM event: low_v")
        self.handle_event("low_v")

    def norm_v(self):
        self.controller.log("SM event: norm_v")
        self.handle_event("norm_v")

    def full_v(self):
        self.controller.log("SM event: full_v")
        self.handle_event("full_v")

    def pow_on(self):
        self.controller.log("SM event: pow_on")
        self.handle_event("pow_on")

    def pow_off(self):
        self.controller.log("SM event: pow_off")
        self.handle_event("pow_off")

    def alert(self):
        self.controller.log("SM event: alert")
        self.handle_event("alert")

    def error(self):
        self.controller.log("SM event: error")
        self.handle_event("error")

    def clear(self):
        self.controller.log("SM event: clear")
        self.handle_event("clear")

import unittest

from bms.states.alert import AlertState
from bms.states.charge import ChargeState
from bms.states.error import ErrorState
from bms.states.eval import EvalState
from bms.states.empty import EmptyState
from bms.states.full import FullState
from bms.states.machine import Statemachine
from bms.states.normal import NormalState
from bms.states.prechg import PreChgState
from test.mock_controller import MockController
from test.states.mock_state import MockState


class StatemachineTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.sm = Statemachine(self.controller)
        self.sm.setup()

    def test_creation(self):
        self.assertEqual(self.controller, self.sm.controller)

    def test_start_state(self):
        self.assertEqual(EvalState, self.sm.state.__class__)

    def test_eval_to_life_support(self):
        self.sm.low_v()
        self.assertEqual(EmptyState, self.sm.state.__class__)

    def test_life_support_to_precharge(self):
        self.sm.low_v()
        self.sm.pow_on()
        self.assertEqual(PreChgState, self.sm.state.__class__)

    def test_eval_to_charge(self):
        self.sm.pow_on()
        self.assertEqual(ChargeState, self.sm.state.__class__)

    def test_eval_to_normal(self):
        self.sm.norm_v()
        self.assertEqual(NormalState, self.sm.state.__class__)

    def test_life_saver_to_normal(self):
        self.sm.low_v()
        self.sm.norm_v()
        self.assertEqual(NormalState, self.sm.state.__class__)

    def test_charge_to_normal(self):
        self.sm.pow_on()
        self.sm.pow_off()
        self.assertEqual(NormalState, self.sm.state.__class__)

    def test_precharge_to_lifesaver(self):
        self.sm.low_v()
        self.sm.pow_on()
        self.sm.pow_off()
        self.assertEqual(EmptyState, self.sm.state.__class__)

    def test_precharge_to_charge(self):
        self.sm.low_v()
        self.sm.pow_on()
        self.sm.norm_v()
        self.assertEqual(ChargeState, self.sm.state.__class__)

    def test_normal_to_alert_and_back(self):
        self.sm.norm_v()
        self.sm.alert()
        self.assertEqual(AlertState, self.sm.state.__class__)
        self.sm.clear()
        self.assertEqual(EvalState, self.sm.state.__class__)

    def test_naormal_to_error_and_back_to_eval(self):
        self.sm.norm_v()
        self.sm.error()
        self.assertEqual(ErrorState, self.sm.state.__class__)
        self.sm.clear()
        self.assertEqual(EvalState, self.sm.state.__class__)

    def test_states_are_entered_and_exited(self):
        start = MockState()
        end = MockState()
        action_called = False

        def foey():
            nonlocal action_called
            action_called = True

        self.sm.trans = {(start, "foo"): (end, foey)}
        self.sm.state = start
        self.sm.handle_event("foo")
        
        self.assertEqual(end, self.sm.state)
        self.assertEqual(True, action_called)
        self.assertEqual(True, start.exited)
        self.assertEqual(True, end.entered)

    def test_fully_charged_state(self):
        self.sm.pow_on()
        self.sm.full_v()
        self.assertEqual(FullState, self.sm.state.__class__)

    def test_full_to_charge(self):
        self.sm.pow_on()
        self.sm.full_v()
        self.sm.norm_v()
        self.assertEqual(ChargeState, self.sm.state.__class__)

    def test_full_to_normal(self):
        self.sm.pow_on()
        self.sm.full_v()
        self.sm.pow_off()
        self.assertEqual(NormalState, self.sm.state.__class__)

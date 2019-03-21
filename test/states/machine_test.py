import unittest

from bms.states.boot import BootState
from bms.states.charge import ChargeState
from bms.states.eval import EvalState
from bms.states.lifesaver import LifeSaverState
from bms.states.machine import Statemachine
from bms.states.normal import NormalState
from bms.states.precharge import PrechargeState
from test.states.mock_context import MockContext


class StatemachineTest(unittest.TestCase):

    def setUp(self):
        self.context = MockContext()
        self.sm = Statemachine(self.context)

    def test_creation(self):
        self.assertEqual(self.context, self.sm.context)

    def test_start_state(self):
        self.assertEqual(BootState, self.sm.state.__class__)

    def test_start_state_booted(self):
        self.sm.tick(1)
        self.assertEqual(EvalState, self.sm.state.__class__)
        
    def test_eval_to_life_support(self):
        self.sm.tick(1)
        self.sm.low_v()
        self.assertEqual(LifeSaverState, self.sm.state.__class__)

    def test_life_support_to_precharge(self):
        self.sm.tick(1)
        self.sm.low_v()
        self.sm.pow_on()
        self.assertEqual(PrechargeState, self.sm.state.__class__)

    def test_eval_to_charge(self):
        self.sm.tick(1)
        self.sm.pow_on()
        self.assertEqual(ChargeState, self.sm.state.__class__)

    def test_eval_to_normal(self):
        self.sm.tick(1)
        self.sm.norm_v()
        self.assertEqual(NormalState, self.sm.state.__class__)

    def test_life_saver_to_normal(self):
        self.sm.tick(1)
        self.sm.low_v()
        self.sm.norm_v()
        self.assertEqual(NormalState, self.sm.state.__class__)

    def test_charge_to_normal(self):
        self.sm.tick(1)
        self.sm.pow_on()
        self.sm.pow_off()
        self.assertEqual(NormalState, self.sm.state.__class__)

    def test_precharge_to_lifesaver(self):
        self.sm.tick(1)
        self.sm.low_v()
        self.sm.pow_on()
        self.sm.pow_off()
        self.assertEqual(LifeSaverState, self.sm.state.__class__)

    def test_precharge_to_charge(self):
        self.sm.tick(1)
        self.sm.low_v()
        self.sm.pow_on()
        self.sm.norm_v()
        self.assertEqual(ChargeState, self.sm.state.__class__)
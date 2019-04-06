import unittest

from bms import util
from bms.conf import CONF
from bms.hardware import Hardware
from test.mock_clock import MockClock
from test.mock_controller import MockController


class HardwareTest(unittest.TestCase):

    def setUp(self):
        util.clock = MockClock()
        self.controller = MockController()
        self.driver = self.controller.driver
        self.bq = self.controller.bq
        self.hardware = Hardware(self.controller)

    def test_calibrate_pack_v(self):
        self.driver.adc_samples = [5, 2050]
        self.hardware.calibrate_pack_v()

        self.assertEqual(5, CONF.PACK_V_OFFSET)
        self.assertAlmostEqual(0.01819, CONF.PACK_V_GAIN, 3)

    def test_balavcers(self):
        self.hardware.test_balancers()

        for cell in self.controller.cells:
            self.assertEqual(False, cell.balancing)





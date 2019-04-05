import unittest

from bms.driver import Driver
from test.mock_pins import MockPin, MockADC


class DriverTest(unittest.TestCase):

    def setUp(self):
        self.cp_en = MockPin()
        self.pmon_en = MockPin()
        self.pchg_en = MockPin()
        self.packdiv = MockADC()
        self.driver = Driver(self.cp_en, self.pmon_en, self.pchg_en, self.packdiv)

    def test_creation(self):
        self.assertEqual(self.cp_en, self.driver._cp_en)
        self.assertEqual(self.pmon_en, self.driver._pmon_en)
        self.assertEqual(self.pchg_en, self.driver._pchg_en)
        self.assertEqual(self.packdiv, self.driver._packdiv)

    def test_charge_pump(self):
        self.driver.setup()
        self.assertEqual(False, self.driver.chargepump())
        self.driver.chargepump(True)
        self.assertEqual(True, self.driver.chargepump())

    def test_precharge(self):
        self.driver.setup()
        self.assertEqual(False, self.driver.precharge())
        self.driver.precharge(True)
        self.assertEqual(True, self.driver.precharge())

    def test_pack_monitor(self):
        self.driver.setup()
        self.assertEqual(False, self.driver.packmonitor())
        self.driver.packmonitor(True)
        self.assertEqual(True, self.driver.packmonitor())

    def test_pack_voltage(self):
        cases = [(5, 0.0),
                 # (790, 10.0),
                 # (1375, 20.0),
                 # (1965, 30.0),
                 (2075, 36.3)
                 # (2550, 40.0),
                 # (3140, 50.0)
                 ]
        for case in cases:
            adc = case[0]
            self.packdiv.value = adc
            calculated = self.driver.pack_voltage()
            measured = case[1]
            self.assertEqual(round(measured * 10), round(calculated * 10))

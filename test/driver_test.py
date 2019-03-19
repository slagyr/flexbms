import unittest

from bms.driver import Driver
from test.mock_pins import MockDPin, MockAPin


class DriverTest(unittest.TestCase):

    def setUp(self):
        self.cp_en = MockDPin()
        self.pmon_en = MockDPin()
        self.pchg_en = MockDPin()
        self.packdiv = MockAPin()
        self.driver = Driver(self.cp_en, self.pmon_en, self.pchg_en, self.packdiv)

    def test_creation(self):
        self.assertEqual(self.cp_en, self.driver._cp_en)
        self.assertEqual(self.pmon_en, self.driver._pmon_en)
        self.assertEqual(self.pchg_en, self.driver._pchg_en)
        self.assertEqual(self.packdiv, self.driver._packdiv)

    def test_setup(self):
        self.driver.setup()

        self.assertEqual("output", self.driver._cp_en.direction)
        self.assertEqual("output", self.driver._pchg_en.direction)
        self.assertEqual("output", self.driver._pmon_en.direction)

    def test_charge_pump(self):
        self.driver.setup()
        self.assertEqual(False, self.driver.get_cp_en())
        self.driver.set_cp_en(True)
        self.assertEqual(True, self.driver.get_cp_en())

    def test_precharge(self):
        self.driver.setup()
        self.assertEqual(False, self.driver.get_pchg_en())
        self.driver.set_pchg_en(True)
        self.assertEqual(True, self.driver.get_pchg_en())

    def test_pack_monitor(self):
        self.driver.setup()
        self.assertEqual(False, self.driver.get_pmon_en())
        self.driver.set_pmon_en(True)
        self.assertEqual(True, self.driver.get_pmon_en())
        
    def test_pack_voltage(self):
        cases = [(934, 0.0),
                 (10088, 10.0),
                 (19290, 20.0),
                 (28560, 30.0),
                 (32167, 34.0),
                 (36793, 39.0),
                 (37731, 40.0),
                 (38684, 41.0),
                 (39568, 42.0),
                 (46888, 50.0),
                 (47869, 51.0)]
        for case in cases:
            adc = case[0]
            self.packdiv.value = adc
            calculated = self.driver.pack_voltage()
            measured = case[1]
            self.assertEqual(round(measured * 10), round(calculated * 10))

import unittest

from bms.pack import Pack
from test.mock_bq import MockBQ
from test.mock_driver import MockDriver


class PackTest(unittest.TestCase):

    def setUp(self):
        self.bq = MockBQ()
        self.driver = MockDriver()
        self.pack = Pack(self.bq, self.driver)

    def test_creation(self):
        self.assertEqual(self.bq, self.pack.bq)
        self.assertEqual(self.driver, self.pack.driver)
        self.assertAlmostEqual(0.0, self.pack.batt_v, 1)
        self.assertAlmostEqual(0.0, self.pack.pack_v, 1)
        self.assertAlmostEqual(0.0, self.pack.amps, 1)


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

    def test_load(self):
        self.bq.stub_batt_v = 36.6
        self.driver.stub_pack_v = 35.5
        self.bq.amperage = -1.23

        self.pack.load()

        self.assertAlmostEqual(36.6, self.pack.batt_v, -1)
        self.assertAlmostEqual(35.5, self.pack.pack_v, -1)
        self.assertAlmostEqual(-1.23, self.pack.amps, -1)

    def test_cache_set_and_reset(self):
        self.assertEqual(False, self.pack.loaded)
        self.pack.load()
        self.assertEqual(True, self.pack.loaded)
        self.pack.expire()
        self.assertEqual(False, self.pack.loaded)



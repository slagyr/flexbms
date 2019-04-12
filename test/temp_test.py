import unittest

from bms.temps import Temps, THERM_TABLE
from test.mock_bq import MockBQ


class TempsTest(unittest.TestCase):

    def setUp(self):
        self.bq = MockBQ()
        self.temps = Temps(self.bq)

    def test_creation(self):
        self.assertEqual(self.bq, self.temps.bq)

    def test_caches_temps_on_load(self):
        bq = self.bq
        bq.stub_therms = [10000, 8313, 6940]

        self.assertEqual(0, self.temps.temp1)
        self.assertEqual(0, self.temps.temp2)
        self.assertEqual(0, self.temps.temp3)

        self.temps.load()

        self.assertEqual(25.0, self.temps.temp1)
        self.assertEqual(30.0, self.temps.temp2)
        self.assertEqual(35.0, self.temps.temp3)

    def test_therm_r_to_c(self):
        for (r, t) in THERM_TABLE:
            self.assertEqual(t, self.temps.therm_r_to_c(r), str(r))

        # resistance values are interpolated between table values
        self.assertAlmostEqual(27.5, self.temps.therm_r_to_c(9156.5), 1)

    def test_themister_1(self):
        self.bq.stub_therms[0] = 10000

        self.assertAlmostEqual(25.0, self.temps.read_temp1(), 1)

    def test_themister_2(self):
        self.bq.stub_therms[1] = 8313

        self.assertAlmostEqual(30.0, self.temps.read_temp2(), 1)

    def test_themister_3(self):
        self.bq.stub_therms[2] = 6940

        self.assertAlmostEqual(35.0, self.temps.read_temp3(), 1)

    def test_cache_set_and_reset(self):
        self.assertEqual(False, self.temps.loaded)
        self.temps.load()
        self.assertEqual(True, self.temps.loaded)
        self.temps.expire()
        self.assertEqual(False, self.temps.loaded)
        
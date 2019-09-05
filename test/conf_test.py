import os
import unittest

from bms.conf import Config, CONF_FILE


class ConfifTest(unittest.TestCase):

    def setUp(self):
        self.conf = Config()
        if os.path.exists(CONF_FILE):
            os.remove(CONF_FILE)

    def test_cell_defaults(self):
        self.assertEqual(10, self.conf.CELL_SERIES)
        self.assertAlmostEqual(4.2, self.conf.CELL_MAX_V, 1)
        self.assertAlmostEqual(2.5, self.conf.CELL_MIN_V, 1)

    def test_bq_defaults(self):
        self.assertEqual(5, self.conf.BQ_CRC_ATTEMPTS)
        self.assertEqual(1, self.conf.BQ_RSNS)
        self.assertEqual(0x1, self.conf.BQ_SCD_DELAY)
        self.assertEqual(0x2, self.conf.BQ_SCD_THRESH)
        self.assertEqual(0x3, self.conf.BQ_OCD_DELAY)
        self.assertEqual(0x8, self.conf.BQ_OCD_THRESH)
        self.assertEqual(0x2, self.conf.BQ_UV_DELAY)
        self.assertEqual(0x1, self.conf.BQ_OV_DELAY)

    def test_balance_defaults(self):
        self.assertEqual(True, self.conf.BALANCE_ENABLED)
        self.assertAlmostEqual(0.01, self.conf.BALANCE_THRESH, 2)


    def test_saving_to_file(self):
        self.conf.save()
        self.assertEqual(True, os.path.exists(CONF_FILE))
        with open(CONF_FILE, "r") as f:
            lines = f.readlines()

        # print it out
        # for line in lines:
        #     print(line[:-1])

        self.assertIn("CELL_SERIES: 10\n", lines)

    def test_reading_from_file(self):
        with open(CONF_FILE, "w") as f:
            f.write("CELL_SERIES: 25\n")
            f.write("BALANCE_ENABLED: False\n")

        self.conf.load()
        self.assertEqual(25, self.conf.CELL_SERIES)
        self.assertEqual(False, self.conf.BALANCE_ENABLED)


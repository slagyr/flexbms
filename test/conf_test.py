import os
import tempfile
import unittest

from bms import conf
from bms.conf import CONF


class ConfTest(unittest.TestCase):

    def setUp(self):
        CONF.reset()
        self.conf_filename = tempfile.gettempdir() + "/bms_test.conf"
        if os.path.exists(self.conf_filename):
            os.remove(self.conf_filename)
        conf.CONF_FILE = self.conf_filename

    def test_cell_defaults(self):
        self.assertEqual(10, CONF.CELL_COUNT)
        self.assertAlmostEqual(4.2, CONF.CELL_MAX_V, 1)
        self.assertAlmostEqual(2.5, CONF.CELL_MIN_V, 1)

    def test_bq_defaults(self):
        self.assertEqual(5, CONF.BQ_CRC_ATTEMPTS)
        self.assertEqual(1, CONF.BQ_RSNS)
        self.assertEqual(0x1, CONF.BQ_SCD_DELAY)
        self.assertEqual(0x2, CONF.BQ_SCD_THRESH)
        self.assertEqual(0x3, CONF.BQ_OCD_DELAY)
        self.assertEqual(0x8, CONF.BQ_OCD_THRESH)
        self.assertEqual(0x2, CONF.BQ_UV_DELAY)
        self.assertEqual(0x1, CONF.BQ_OV_DELAY)

    def test_balance_defaults(self):
        self.assertEqual(True, CONF.BALANCE_ENABLED)
        self.assertAlmostEqual(0.01, CONF.BALANCE_THRESH, 2)


    def test_saving_to_file(self):
        CONF.save()
        self.assertEqual(True, os.path.exists(self.conf_filename))
        with open(self.conf_filename, "r") as f:
            lines = f.readlines()
        self.assertIn("CELL_COUNT: 10\n", lines)

    def test_reading_from_file(self):
        with open(self.conf_filename, "w") as f:
            f.write("CELL_COUNT: 25\n")
            f.write("BALANCE_ENABLED: False\n")

        CONF.load()
        self.assertEqual(25, CONF.CELL_COUNT)
        self.assertEqual(False, CONF.BALANCE_ENABLED)
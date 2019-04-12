import os
import unittest
import tempfile

from bms import util
from bms.cells import Cells
from bms.logger import Logger
from bms.pack import Pack
from bms.temps import Temps
from test.mock_clock import MockClock


class LoggerTest(unittest.TestCase):

    def setUp(self):
        self.log_dir = tempfile.gettempdir() + "/log"
        for log in ["msg.log", "cell.csv", "temp.csv", "pack.csv"]:
            self.delete_log_file(log)
        self.logger = Logger(self.log_dir)
        self.logger.setup()
        self.clock = MockClock(1234)
        util.clock = self.clock

    def delete_log_file(self, name):
        path = self.log_dir + "/" + name
        if os.path.exists(path):
            os.remove(path)

    def readlines(self, name):
        with open(self.log_dir + "/" + name, "r") as f:
            return f.readlines()

    def tearDown(self):
        self.logger.close()

    def test_without_path(self):
        logger = Logger()
        self.assertTrue("log", logger.path)

    def test_with_path_and_setup(self):
        self.assertTrue(self.log_dir, self.logger.path)
        self.assertEqual(True, os.path.exists(self.log_dir))
        self.assertIsNotNone(self.logger.cell_log)
        self.assertIsNotNone(self.logger.pack_log)
        self.assertIsNotNone(self.logger.temp_log)
        self.assertIsNotNone(self.logger.msg_log)


    def test_logging_message(self):
        self.logger.msg("hello")
        lines = self.readlines("msg.log")
        self.assertEqual(1, len(lines))
        self.assertEqual("1234 hello\n", lines[0])

    def test_logging_message_with_multiple_args(self):
        self.logger.msg("hello", 1, 2, 3.14)
        lines = self.readlines("msg.log")
        self.assertEqual(1, len(lines))
        self.assertEqual("1234 hello 1 2 3.14\n", lines[0])

    def test_logging_cell_voltages(self):
        cells = Cells(10)
        for cell in cells:
            cell.voltage = 2.5 + (cell.id * 0.1)

        self.logger.cells(cells)
        lines = self.readlines("cell.csv")
        self.assertEqual(1, len(lines))
        self.assertEqual("1234,2.6,2.7,2.8,3.0,3.1,3.2,3.5,3.6,3.7,4.0\n", lines[0])

    def test_logging_temps(self):
        temps = Temps("bq")
        temps.temp1 = 20.2
        temps.temp2 = 30.4
        temps.temp3 = 40.4

        self.logger.temps(temps)
        lines = self.readlines("temp.csv")
        self.assertEqual(1, len(lines))
        self.assertEqual("1234,20.2,30.4,40.4\n", lines[0])

    def test_logging_pack(self):
        pack = Pack("bq", "driver")
        pack.batt_v = 36.3
        pack.pack_v = 35.5
        pack.amps = -5.4
        self.logger.pack(pack)
        lines = self.readlines("pack.csv")
        self.assertEqual(1, len(lines))
        self.assertEqual("1234,36.3,35.5,-5.4\n", lines[0])
    


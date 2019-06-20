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
        self.logfile = tempfile.gettempdir() + "/bms.log"
        if os.path.exists(self.logfile):
            os.remove(self.logfile)
        self.logger = Logger(self.logfile)
        self.logger.setup()
        self.clock = MockClock(1234)
        util.clock = self.clock

    def delete_log_file(self, name):
        path = self.log_dir + "/" + name
        if os.path.exists(path):
            os.remove(path)

    def readlines(self):
        with open(self.logfile, "r") as f:
            return f.readlines()

    def tearDown(self):
        self.logger.close()

    def test_without_path(self):
        logger = Logger()
        self.assertEqual("bms.log", logger.logfile)

    def test_with_path_and_setup(self):
        self.assertEqual(self.logfile, self.logger.logfile)

    def test_logging_message(self):
        self.logger.info("hello")
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("info: hello\n", lines[0])

    def test_logging_message_with_multiple_args(self):
        self.logger.info("hello", 1, 2, 3.14)
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("info: hello 1 2 3.14\n", lines[0])

    def test_logging_cell_voltages(self):
        cells = Cells("bq", 10)
        for cell in cells:
            cell.voltage = 2.5 + (cell.id * 0.1)

        self.logger.cells(cells)
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("cells: 2.6,2.7,2.8,3.0,3.1,3.2,3.5,3.6,3.7,4.0\n", lines[0])

    def test_logging_temps(self):
        temps = Temps("bq")
        temps.temp1 = 20.2
        temps.temp2 = 30.4
        temps.temp3 = 40.4

        self.logger.temps(temps)
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("temps: 20.2,30.4,40.4\n", lines[0])

    def test_logging_pack(self):
        pack = Pack("bq", "driver")
        pack.batt_v = 36.3
        pack.pack_v = 35.5
        pack.amps_in = -5.4
        self.logger.pack(pack)
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("pack: 36.3,35.5,-5.4\n", lines[0])

    def test_logging_tick(self):
        self.logger.tick(1, 1234)
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("tick: 1, 1234\n", lines[0])
    


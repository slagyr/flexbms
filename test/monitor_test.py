import os
import tempfile
import unittest

from bms import bq
from bms.cells import Cells
from bms.monitor import Monitor
from bms.pack import Pack
from bms.temps import Temps


class MonitorTest(unittest.TestCase):

    def setUp(self):
        self.outfile = tempfile.gettempdir() + "/monitor.log"
        if os.path.exists(self.outfile):
            os.remove(self.outfile)
        self.out = open(self.outfile, "a")
        self.monitor = Monitor(self.out)

    def tearDown(self):
        self.out.close()

    # def delete_log_file(self, name):
    #     path = self.outfile + "/" + name
    #     if os.path.exists(path):
    #         os.remove(path)

    def readlines(self):
        self.out.close()
        with open(self.outfile, "r") as f:
            return f.readlines()

    def test_creation_default(self):
        self.assertIs(self.out, self.monitor.out)

    def test_monitoring_cell_voltages(self):
        cells = Cells("bq", 10)
        for cell in cells:
            cell.voltage = 2.5 + (cell.id * 0.1)

        self.monitor.cells(cells)
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("cells: 2.6,2.7,2.8,3.0,3.1,3.2,3.5,3.6,3.7,4.0\n", lines[0])

    def test_monitoring_temps(self):
        temps = Temps("bq")
        temps.temp1 = 20.2
        temps.temp2 = 30.4
        temps.temp3 = 40.4

        self.monitor.temps(temps)
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("temps: 20.2,30.4,40.4\n", lines[0])

    def test_monitoring_pack(self):
        pack = Pack("bq", "driver")
        pack.batt_v = 36.3
        pack.pack_v = 35.5
        pack.amps_in = -5.4
        self.monitor.pack(pack)
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("pack: 36.3,35.5,-5.4\n", lines[0])

    def test_monitoring_bq_alert(self):
        self.monitor.alert(None, [bq.DEVICE_XREADY,
                                  bq.OVRD_ALERT,
                                  bq.UV,
                                  bq.OV,
                                  bq.SCD,
                                  bq.OCD])
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual(
            "alert: Device Not Ready, Alert Pin Override, Undervoltage, Overvoltage, Discharge Short Circuit, Discharge Overcurrent\n",
            lines[0])

    def test_monitoring_custom(self):
        self.monitor.alert("My Alert", [])
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("alert: My Alert\n", lines[0])

    def test_monitoring_custom_and_bq_fault(self):
        self.monitor.alert("My Alert", [bq.UV])
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("alert: My Alert, Undervoltage\n", lines[0])

    def test_monitoring_exception(self):
        self.monitor.error("foo")
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("error: foo\n", lines[0])

    def test_monitoring_state(self):
        self.monitor.state("foo")
        lines = self.readlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("state: foo\n", lines[0])

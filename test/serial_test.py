import unittest

from bms import bq
from bms.cells import Cells
from bms.serial import Serial
from bms.pack import Pack
from bms.temps import Temps
from test.mock_VCP import MockVCP
from test.mock_controller import MockController
from test.states.mock_machine import MockStatemachine


class SerialTest(unittest.TestCase):

    def setUp(self):
        self.vcp = MockVCP()
        self.controller = MockController()
        self.conf = self.controller.conf
        self.controller.sm = MockStatemachine()
        self.serial = Serial(self.controller, self.vcp)

    def test_creation_default(self):
        self.assertIs(self.controller, self.serial.controller)
        self.assertIs(self.vcp, self.serial.port)

    def test_serialing_cell_voltages(self):
        cells = Cells(self.conf, "bq", 10)
        for cell in cells:
            cell.voltage = 2.5 + (cell.id * 0.1)

        self.serial.cells(cells)
        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual("cells: 2.6,2.7,2.8,3.0,3.1,3.2,3.5,3.6,3.7,4.0\n", self.vcp.output[0])

    def test_serialing_cell_balancing(self):
        cells = Cells(self.conf, "bq", 10)

        self.serial.balance(cells)
        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual("balance: \n", self.vcp.output[0])

        cells[2].balancing = True
        cells[4].balancing = True
        cells[6].balancing = True
        cells[8].balancing = True
        for cell in cells:
            cell.voltage = 2.5 + (cell.id * 0.1)

        self.serial.balance(cells)
        self.assertEqual(2, len(self.vcp.output))
        self.assertEqual("balance: 2,4,6,8\n", self.vcp.output[1])


    def test_serialing_temps(self):
        temps = Temps("bq")
        temps.temp1 = 20.2
        temps.temp2 = 30.4
        temps.temp3 = 40.4

        self.serial.temps(temps)
        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual("temps: 20.2,30.4,40.4\n", self.vcp.output[0])

    def test_serialing_pack(self):
        pack = Pack("bq", "driver")
        pack.batt_v = 36.3
        pack.pack_v = 35.5
        pack.amps_in = -5.4
        self.serial.pack(pack)
        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual("pack: 36.3,35.5,-5.4\n", self.vcp.output[0])

    def test_serialing_bq_alert(self):
        self.serial.alert(None, [bq.DEVICE_XREADY,
                                  bq.OVRD_ALERT,
                                  bq.UV,
                                  bq.OV,
                                  bq.SCD,
                                  bq.OCD])
        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual(
            "alert: Device Not Ready, Alert Pin Override, Undervoltage, Overvoltage, Discharge Short Circuit, Discharge Overcurrent\n",
            self.vcp.output[0])

    def test_serialing_custom(self):
        self.serial.alert("My Alert", [])
        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual("alert: My Alert\n", self.vcp.output[0])

    def test_serialing_custom_and_bq_fault(self):
        self.serial.alert("My Alert", [bq.UV])
        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual("alert: My Alert, Undervoltage\n", self.vcp.output[0])

    def test_serialing_exception(self):
        self.serial.error("foo")
        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual("error: foo\n", self.vcp.output[0])

    def test_serialing_state(self):
        self.serial.state("foo")
        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual("state: foo\n", self.vcp.output[0])

    def test_silencing(self):
        cells = Cells(self.conf, "bq", 10)
        self.vcp.input.append("silence")
        self.serial.read()

        self.serial.cells(cells)
        self.assertEqual(0, len(self.vcp.output))

    def test_unsilencing(self):
        cells = Cells(self.conf, "bq", 10)
        self.vcp.input.append("silence")
        self.serial.read()

        self.vcp.input.append("verbose")
        self.serial.read()

        self.serial.cells(cells)
        self.assertEqual(1, len(self.vcp.output))

    def test_clear(self):
        self.vcp.input.append("clear")
        self.serial.read()
        self.assertEqual("clear", self.controller.sm.last_event)

    def test_rest(self):
        self.vcp.input.append("rest")
        self.serial.read()
        self.assertEqual("rest", self.controller.sm.last_event)

    def test_wake(self):
        self.vcp.input.append("wake")
        self.serial.read()
        self.assertEqual("wake", self.controller.sm.last_event)

    def test_shut(self):
        self.vcp.input.append("shut")
        self.serial.read()
        self.assertEqual("shut", self.controller.sm.last_event)

    def test_state_qmark(self):
        self.controller.sm.state = self.controller.sm._prechg

        self.vcp.input.append("state?")
        self.serial.read()

        self.assertEqual(1, len(self.vcp.output))
        self.assertEqual("state: PreChgState\n", self.vcp.output[0])

    def test_set_cell_full_v(self):
        self.vcp.input.append("set_cell_full_v, 3.14")
        self.serial.read()

        self.assertAlmostEqual(3.14, self.conf.CELL_FULL_V, 2)
        self.assertEqual(True, self.conf.was_saved)

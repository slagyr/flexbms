from bms import bq
from bms.util import log


class Serial:

    def __init__(self, controller, port):
        self.controller = controller
        self.port = port
        self.silent = False

    def setup(self):
        self.cell_full_v()

    def _append(self, l):
        if not self.silent:
            self.port.write(l)

    def cells(self, cells):
        line = "cells: " + str(cells[0].voltage)
        for cell in cells[1:]:
            line += "," + str(cell.voltage)
        self._append(line + "\n")

    def balance(self, cells):
        line = "balance: "
        balancing = []
        for cell in cells[1:]:
            if cell.balancing:
                balancing.append(str(cell.index))
        self._append(line + ",".join(balancing) + "\n")

    def temps(self, temps):
        line = "temps: " + str(temps.temp1) + "," + str(temps.temp2) + "," + str(temps.temp3) + "\n"
        self._append(line)

    def pack(self, pack):
        line = "pack: " + str(pack.batt_v) + "," + str(pack.pack_v) + "," + str(pack.amps_in) + "\n"
        self._append(line)

    def bq_fault_to_string(self, fault):
        if fault == bq.DEVICE_XREADY:
            return "Device Not Ready"
        elif fault == bq.OVRD_ALERT:
            return "Alert Pin Override"
        elif fault == bq.UV:
            return "Undervoltage"
        elif fault == bq.OV:
            return "Overvoltage"
        elif fault == bq.SCD:
            return "Discharge Short Circuit"
        elif fault == bq.OCD:
            return "Discharge Overcurrent"
        else:
            return "UNKNOWN ALERT!!!"

    def alert(self, custom, bq_faults):
        line = "alert: "
        names = []
        if custom:
            names.append(custom)
        names += map(self.bq_fault_to_string, bq_faults)
        line += ", ".join(names)
        line += "\n"
        self._append(line)

    def error(self, msg):
        line = "error: " + str(msg) + "\n"
        self._append(line)

    def state(self, name):
        line = "state: " + str(name) + "\n"
        self._append(line)

    def cell_full_v(self):
        line = "cell_full_v: " + "{0:1.2f}".format(self.controller.conf.CELL_FULL_V) + "\n"
        self._append(line)

    def read(self):
        line = self.port.readline()
        if line is not None:
            cmd = line.decode("utf-8").strip()
            self.process_command(cmd)

    def process_command(self, cmd):
        if cmd == "silence":
            self.silent = True
        elif cmd == "verbose":
            self.silent = False
        elif cmd == "clear":
            self.controller.sm.clear()
        elif cmd == "rest":
            self.controller.sm.rest()
        elif cmd == "wake":
            self.controller.sm.wake()
        elif cmd == "shut":
            self.controller.sm.shut()
        elif cmd == "state?":
            self.state(self.controller.sm.state.__class__.__name__)
        elif cmd.startswith("set_cell_full_v"):
            self.set_cell_full_v(cmd)
        elif cmd == "reboot":
            import machine
            machine.reset()

    def set_cell_full_v(self, cmd):
        tokens = cmd.split(",")
        str_val = tokens[1].strip()
        volts = float(str_val)
        log("setting CELL_FULL_V:", volts)

        conf = self.controller.conf
        conf.CELL_FULL_V = volts
        conf.save()
        self.cell_full_v()





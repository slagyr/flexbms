import sys

from bms import bq


class Monitor:

    def __init__(self, out):
        self.out = out

    def _append(self, l):
        self.out.write(l)

    def cells(self, cells):
        line = "cells: " + str(cells[0].voltage)
        for cell in cells[1:]:
            line += "," + str(cell.voltage)
        self._append(line + "\n")

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

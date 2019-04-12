import os

from bms import util


class Logger:
    def __init__(self, path="log"):
        self.path = path
        self.cell_log = None
        self.temp_log = None
        self.pack_log = None
        self.msg_log = None

    def setup(self):
        try:
            os.stat(self.path)
        except OSError as e:
            os.mkdir(self.path)
        self.cell_log = open(self.path + "/cell.csv", "a+")
        self.temp_log = open(self.path + "/temp.csv", "a+")
        self.pack_log = open(self.path + "/pack.csv", "a+")
        self.msg_log = open(self.path + "/msg.log", "a+")

    def close(self):
        if self.cell_log:
            self.cell_log.close()
        if self.temp_log:
            self.temp_log.close()
        if self.pack_log:
            self.pack_log.close()
        if self.msg_log:
            self.msg_log.close()

    def _append_line(self, f, l):
        f.write(l)
        f.flush()

    def msg(self, *argv):
        s = str(util.clock.millis()) + " " + str(argv[0])
        for arg in argv[1:]:
            s += " " + str(arg)

        self._append_line(self.msg_log, s + "\n")

    def cells(self, cells):
        line = str(util.clock.millis())
        for cell in cells:
            line += "," + str(cell.voltage)
        self._append_line(self.cell_log, line + "\n")

    def temps(self, temps):
        line = str(util.clock.millis()) + "," + str(temps.temp1) + "," + str(temps.temp2) + "," + str(temps.temp3) + "\n"
        self._append_line(self.temp_log, line)

    def pack(self, pack):
        line = str(util.clock.millis()) + "," + str(pack.batt_v) + "," + str(pack.pack_v) + "," + str(pack.amps) + "\n"
        self._append_line(self.pack_log, line)





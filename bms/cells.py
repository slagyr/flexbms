from bms.conf import *


class Cells:
    def __init__(self, bq, count):
        self.bq = bq
        self.count = count
        if count == 15:
            self.ids = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        elif count == 14:
            self.ids = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15)
        elif count == 13:
            self.ids = (1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15)
        elif count == 12:
            self.ids = (1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15)
        elif count == 11:
            self.ids = (1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 15)
        elif count == 10:
            self.ids = (1, 2, 3, 5, 6, 7, 10, 11, 12, 15)
        elif count == 9:
            self.ids = (1, 2, 5, 6, 7, 10, 11, 12, 15)

        self.voltages = []
        for _ in self.ids:
            self.voltages.append(0)

    def setup(self):
        pass

    def update_voltages(self):
        for i in range(self.count):
            id = self.ids[i]
            v = self.bq.cell_voltage(id)
            self.voltages[i] = v

    # state of charge.  0 => fully discharged, 1 => fully charged
    def soc(self, cell_i):
        v = self.voltages[cell_i]
        return (v - CELL_MIN_V) / (CELL_MAX_V - CELL_MIN_V)


import time

from bms import util
from bms.util import ON_BOARD, log

if not ON_BOARD:
    from bms.util import const

# These values need to be calculated with soldered board
GAIN = 0.0176
OFFSET = 125
# To measure:
#   Turn off BQ CHG_ON and DSH_ON
#   Connected known voltage to Pack+ and -
#   Measure the ADC value


class Driver:
    def __init__(self, cp_en, pmon_en, pchg_en, packdiv):
        self._cp_en = cp_en
        self._pmon_en = pmon_en
        self._pchg_en = pchg_en
        self._packdiv = packdiv

    def setup(self):
        pass

    def get_cp_en(self):
        return self._cp_en.value()

    def set_cp_en(self, on):
        self._cp_en.value(on)

    def get_pchg_en(self):
        return self._pchg_en.value()

    def set_pchg_en(self, on):
        self._pchg_en.value(on)

    def get_pmon_en(self):
        return self._pmon_en.value()

    def set_pmon_en(self, on):
        self._pmon_en.value(on)

    def pack_voltage(self):
        sum = 0
        self.set_pmon_en(True)
        for i in range(10):
            adc = self._packdiv.read()
            sum += adc
        self.set_pmon_en(False)
        avg = sum / 10
        return (avg - OFFSET) * GAIN


# def avg():
# sum = 0
# for i in range(10):
# r = d._packdiv.read()
# # print("r: " + str(r))
# sum += r
# pyb.delay(10)
# return int(sum / 10)
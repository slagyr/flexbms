import time

from bms.util import ON_BOARD
if not ON_BOARD:
    from bms.util import const

# Thes values were painstakingly calculated and tweak using empirical data.  Need a better way.
GAIN = 0.001087
OFFSET = 930
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
        # self._cp_en.switch_to_output()
        # self._pmon_en.switch_to_output()
        # self._pchg_en.switch_to_output()
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
            sum += self._packdiv.value
        self.set_pmon_en(False)
        avg = sum / 10
        return (avg - OFFSET) * GAIN

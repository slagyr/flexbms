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
    def __init__(self, charge_pump_pin, pack_monitor_pin, precharge_pin, pack_divider_adc):
        self._cp_en = charge_pump_pin
        self._pmon_en = pack_monitor_pin
        self._pchg_en = precharge_pin
        self._packdiv = pack_divider_adc
        self.chargepump = self._cp_en.value # getter and setter
        self.precharge = self._pchg_en.value # getter and setter
        self.packmonitor = self._pmon_en.value # getter and setter

    def setup(self):
        pass

    def pack_voltage(self):
        sum = 0
        self.packmonitor(True)
        for i in range(10):
            adc = self._packdiv.read()
            sum += adc
        self.packmonitor(False)
        avg = sum / 10
        return (avg - OFFSET) * GAIN

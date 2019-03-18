class Driver:
    def __init__(self, cp_en, pmon_en, pchg_en, packdiv):
        self._cp_en = cp_en
        self._pmon_en = pmon_en
        self._pchg_en = pchg_en
        self._packdiv = packdiv

    def setup(self):
        self._cp_en.switch_to_output()
        self._pmon_en.switch_to_output()
        self._pchg_en.switch_to_output()

    def get_cp_en(self):
        return self._cp_en.value

    def set_cp_en(self, on):
        self._cp_en.value = on

    def get_pchg_en(self):
        return self._pchg_en.value

    def set_pchg_en(self, on):
        self._pchg_en.value = on

    def get_pmon_en(self):
        return self._pmon_en.value

    def set_pmon_en(self, on):
        self._pmon_en.value = on

    # 0 - 65535
    def read_voltage(self):
        self.set_pmon_en(True)
        adc = self._packdiv.value
        self.set_pmon_en(False)
        ref = self._packdiv.reference_voltage
        return adc / 65535 * ref


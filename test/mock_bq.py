from bms.bq import BQ
from test.mock import Mock


class MockBQ(Mock):
    def __init__(self):
        self.was_setup = False
        self.voltages = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]

        self.adc_gain = None
        self.adc_offset = None
        self.i2c = None
        self.faults = None
        self.cc_ready = None
        self.assert_mock(BQ("I2C"))


    def read_register(self):
        pass


    def read_register_single(self):
        pass


    def read_register_double(self):
        pass


    def write_register(self):
        pass


    def set_reg_bit(self):
        pass


    def get_reg_bit(self):
        pass


    def clear_fault(self):
        pass


    def __enter__(self):
        pass


    def __exit__(self):
        pass


    def check_sys_stat(self):
        pass


    def read_adc_gain(self):
        pass


    def v_to_adc(self):
        pass


    def read_adc_offset(self):
        pass


    def adc_to_v(self):
        pass


    def set_uv_trip(self):
        pass


    def get_uv_trip(self):
        pass


    def set_ov_trip(self):
        pass


    def get_ov_trip(self):
        pass


    def set_protect1(self):
        pass


    def set_protect2(self):
        pass


    def cell_voltage(self, id):
        return self.voltages[id - 1]


    def setup(self):
        self.was_setup = True

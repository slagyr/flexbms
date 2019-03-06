import unittest

from bms.bq76940 import *
from test.mock_bq_i2c import MockBqI2C


class BQ76940Test(unittest.TestCase):

    def setUp(self):
        self.i2c = MockBqI2C()
        self.bq = BQ76940(self.i2c)

    def prep_setup(self):
        self.i2c.scan_result = [0x08] # BQ76940 I@C Address
        self.i2c.registers[0x00] = 0b00000000 # SYS_STAT
        self.i2c.registers[0x04] = 0b00000000 # SYSCTRL1
        self.i2c.registers[0x05] = 0b00000000 # SYSCTRL2
        self.i2c.registers[0x06] = 0b00000000 # PROTECT1
        self.i2c.registers[0x07] = 0b00000000 # PROTECT2
        self.i2c.registers[0x09] = 0b00000000 # OV_TRIP
        self.i2c.registers[0x0A] = 0b00000000 # UV_TRIP
        self.i2c.registers[0x50] = 0b00000000 # ADCGAIN1
        self.i2c.registers[0x59] = 0b00000000 # ADCGAIN2
        self.i2c.registers[0x51] = 0b00101010 # ADCOFFSET (42)

    def test_creation(self):
        self.assertEqual(self.i2c, self.bq.i2c)

    def test_register_read_single(self):
        self.i2c.registers[0xAB] = 42
        self.i2c.registers[0xAC] = 31
        self.assertEqual(42, self.bq.read_register_single(0xAB))
        self.assertEqual(31, self.bq.read_register_single(0xAC))

    def test_setup_checks_for_address(self):
        self.i2c.scan_result = [0x1, 0x2, 0x3]
        try:
            self.bq.setup()
            self.fail("should complain about missing address")
        except RuntimeError as ex:
            self.assertEqual("BQ address not found in scan", ex.args[0])

    def test_setup_write_magic_0x19_to_CC_CFG(self):
        self.prep_setup()
        self.bq.setup()
        self.assertEqual(0x19, self.i2c.registers[0x0B])

    def test_crc8(self):
        self.assertEqual(122, self.bq.crc8(bytearray([16, 11, 25])))
        self.assertEqual(5, self.bq.crc8(bytearray([16, 4, 255])))
        self.assertEqual(16, self.bq.crc8(bytearray([16, 5, 255])))
        self.assertEqual(66, self.bq.crc8(bytearray([16, 0, 32])))
        self.assertEqual(127, self.bq.crc8(bytearray([16, 10, 170])))
        self.assertEqual(243, self.bq.crc8(bytearray([16, 9, 151])))
        self.assertEqual(234, self.bq.crc8(bytearray([16, 6, 10])))
        self.assertEqual(97, self.bq.crc8(bytearray([16, 7, 56])))
        self.assertEqual(67, self.bq.crc8(bytearray([16, 1, 254])))
        self.assertEqual(74, self.bq.crc8(bytearray([16, 1, 253])))
        self.assertEqual(88, self.bq.crc8(bytearray([16, 1, 251])))
        self.assertEqual(124, self.bq.crc8(bytearray([16, 1, 247])))
        self.assertEqual(52, self.bq.crc8(bytearray([16, 1, 239])))

    def test_setup_enables_ADC(self):
        self.prep_setup()
        self.assertEqual(False, self.bq.get_reg_bit(ADC_EN))

        self.bq.setup()
        self.assertTrue(self.i2c.registers[0x04] & (1 << 4))
        self.assertEqual(True, self.bq.get_reg_bit(ADC_EN))

    def test_setup_enables_CC_continuous(self):
        self.prep_setup()
        self.assertEqual(False, self.bq.get_reg_bit(CC_EN))

        self.bq.setup()
        self.assertTrue(self.i2c.registers[0x05] & (1 << 6))
        self.assertEqual(True, self.bq.get_reg_bit(CC_EN))

    def test_ADCGAIN(self):
        self.prep_setup()
        self.bq.setup()
        self.assertEqual(365, self.bq.adc_gain)

        self.i2c.registers[0x50] = 0b10001100 # ADCGAIN1 with noise
        self.i2c.registers[0x59] = 0b11100001 # ADCGAIN2 with noise
        self.assertEqual(396, self.bq.read_adc_gain())

        self.i2c.registers[0x50] = 0b01000100 # ADCGAIN1 with noise
        self.i2c.registers[0x59] = 0b11100010 # ADCGAIN2 with noise
        self.assertEqual(380, self.bq.read_adc_gain())

    def test_ADCOFFSET(self):
        self.prep_setup()
        self.bq.setup()
        self.assertEqual(42, self.bq.adc_offset)

        self.i2c.registers[0x51] = 0b11111111 # ADCOFFSET
        self.assertEqual(-1, self.bq.read_adc_offset())

        self.i2c.registers[0x51] = 0b01111111 # ADCOFFSET
        self.assertEqual(127, self.bq.read_adc_offset())

        self.i2c.registers[0x51] = 0b10000000 # ADCOFFSET
        self.assertEqual(-128, self.bq.read_adc_offset())

    def test_adc_to_v(self):
        self.bq.adc_gain = 380
        self.bq.adc_offset = 30
        self.assertAlmostEqual(2.365, self.bq.adc_to_v(6144), 3)
        self.assertAlmostEqual(3.052, self.bq.adc_to_v(7952), 3)
        
    def test_OV_TRIP(self):
        self.prep_setup()
        self.bq.setup()
        self.assertEqual(0b11000111, self.i2c.registers[0x09])
        self.assertAlmostEqual(4.2, self.bq.get_ov_trip(), 1)

        self.bq.adc_gain = 380
        self.bq.adc_offset = 36
        self.bq.set_ov_trip(3.456)
        self.assertEqual(0b00110010, self.i2c.registers[0x09])
        self.assertAlmostEqual(3.456, self.bq.get_ov_trip(), 1)

    def test_UV_TRIP(self):
        self.prep_setup()
        self.bq.setup()
        self.assertEqual(0b10100100, self.i2c.registers[0x0A])
        self.assertAlmostEqual(2.5, self.bq.get_uv_trip(), 1)

        self.bq.adc_gain = 380
        self.bq.adc_offset = 36
        self.bq.set_uv_trip(2.718)
        self.assertEqual(0b10111001, self.i2c.registers[0x0A])
        self.assertAlmostEqual(2.718, self.bq.get_uv_trip(), 1)

    def test_PROTECT1_SCD_values(self):
        self.prep_setup()
        self.bq.setup()

        protect1 = self.i2c.registers[0x06]
        rsns = (protect1 & 0b10000000) >> 7
        self.assertEqual(RSNS_BIT, rsns)

        scd_delay = (protect1 & 0b00011000) >> 3
        self.assertEqual(SCD_DELAY, scd_delay)

        scd_thresh = protect1 & 0b00000111
        self.assertEqual(SCD_THRESH, scd_thresh)

    def test_PROTECT2_OCD_values(self):
        self.prep_setup()
        self.bq.setup()

        protect2 = self.i2c.registers[0x07]
        ocd_delay = (protect2 & 0b1110000) >> 4
        self.assertEqual(OCD_DELAY, ocd_delay)

        ocd_thresh = (protect2 & 0b1111)
        self.assertEqual(OCD_THRESH, ocd_thresh)
        
    def test_sys_stat_no_faults(self):
        self.i2c.registers[0x0] = 0b00000000
        self.bq.check_sys_stat()
        self.assertFalse(self.bq.cc_ready)
        self.assertEqual([], self.bq.faults)

        self.i2c.registers[0x0] = 0b10000000
        self.bq.check_sys_stat()
        self.assertTrue(self.bq.cc_ready)
        self.assertEqual([], self.bq.faults)

        self.i2c.registers[0x0] = 0b10111111
        self.bq.check_sys_stat()
        self.assertTrue(self.bq.cc_ready)
        self.assertTrue(self.bq.faults)
        self.assertEqual([OVRD_ALERT, UV, OV, SCD, OCD], self.bq.faults)

    def test_clear_fault(self):
        self.i2c.registers[0x0] = 0
        self.bq.faults = [OVRD_ALERT, UV, OV, SCD, OCD]
        self.bq.clear_fault(OV)
        self.assertEqual(0b00100100, self.i2c.registers[0x0])
        self.assertEqual([OVRD_ALERT, UV, SCD, OCD], self.bq.faults)

        self.bq.clear_fault(OCD)
        self.assertEqual(0b00100001, self.i2c.registers[0x0])
        self.assertEqual([OVRD_ALERT, UV, SCD], self.bq.faults)

        self.bq.clear_fault(OVRD_ALERT)
        self.assertEqual(0b00110000, self.i2c.registers[0x0])
        self.assertEqual([UV, SCD], self.bq.faults)

        self.bq.clear_fault(UV)
        self.assertEqual(0b00101000, self.i2c.registers[0x0])
        self.assertEqual([SCD], self.bq.faults)

        self.bq.clear_fault(SCD)
        self.assertEqual(0b00100010, self.i2c.registers[0x0])
        self.assertEqual([], self.bq.faults)
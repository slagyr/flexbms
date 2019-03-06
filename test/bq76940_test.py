import unittest

from bms.bq76940 import *
from test.mock_bq_i2c import MockBqI2C


class BQ76940Test(unittest.TestCase):

    def setUp(self):
        self.i2c = MockBqI2C()
        self.bq = BQ76940(self.i2c)

    def prep_setup(self):
        self.i2c.scan_result = [0x08] # BQ76940 I@C Address
        self.i2c.registers[0x04] = 0b00000000 # SYSCTRL1
        self.i2c.registers[0x05] = 0b00000000 # SYSCTRL2
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
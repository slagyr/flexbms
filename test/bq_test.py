import unittest

from bms.bq import *
from bms.cells import Cells
from test.mock_bq_i2c import MockBqI2C


class BQ76940Test(unittest.TestCase):

    def setUp(self):
        self.i2c = MockBqI2C()
        self.bq = BQ(self.i2c)

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
        self.bq.setup()
        self.assertEqual(0x19, self.i2c.registers[0x0B])

    def test_crc8(self):
        self.assertEqual(122, crc8(bytearray([16, 11, 25])))
        self.assertEqual(5, crc8(bytearray([16, 4, 255])))
        self.assertEqual(16, crc8(bytearray([16, 5, 255])))
        self.assertEqual(66, crc8(bytearray([16, 0, 32])))
        self.assertEqual(127, crc8(bytearray([16, 10, 170])))
        self.assertEqual(243, crc8(bytearray([16, 9, 151])))
        self.assertEqual(234, crc8(bytearray([16, 6, 10])))
        self.assertEqual(97, crc8(bytearray([16, 7, 56])))
        self.assertEqual(67, crc8(bytearray([16, 1, 254])))
        self.assertEqual(74, crc8(bytearray([16, 1, 253])))
        self.assertEqual(88, crc8(bytearray([16, 1, 251])))
        self.assertEqual(124, crc8(bytearray([16, 1, 247])))
        self.assertEqual(52, crc8(bytearray([16, 1, 239])))

    def test_setup_disables_ADC(self):
        self.assertEqual(False, self.bq.get_reg_bit(ADC_EN))

        self.bq.setup()
        self.assertEqual(0, self.i2c.registers[0x04] & (1 << 4))
        self.assertEqual(False, self.bq.get_reg_bit(ADC_EN))

    def test_setup_disables_CC_continuous(self):
        self.assertEqual(False, self.bq.get_reg_bit(CC_EN))

        self.bq.setup()
        self.assertEqual(0, self.i2c.registers[0x05] & (1 << 6))
        self.assertEqual(False, self.bq.get_reg_bit(CC_EN))

    def test_ADCGAIN(self):
        self.bq.setup()
        self.assertEqual(365, self.bq.adc_gain)

        self.i2c.registers[0x50] = 0b10001100 # ADCGAIN1 with noise
        self.i2c.registers[0x59] = 0b11100001 # ADCGAIN2 with noise
        self.assertEqual(396, self.bq.read_adc_gain())

        self.i2c.registers[0x50] = 0b01000100 # ADCGAIN1 with noise
        self.i2c.registers[0x59] = 0b11100010 # ADCGAIN2 with noise
        self.assertEqual(380, self.bq.read_adc_gain())

    def test_ADCOFFSET(self):
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
        self.bq.setup()
        self.assertEqual(0b11000111, self.i2c.registers[0x09])
        self.assertAlmostEqual(4.2, self.bq.get_ov_trip(), 1)

        self.bq.adc_gain = 380
        self.bq.adc_offset = 36
        self.bq.set_ov_trip(3.456)
        self.assertEqual(0b00110010, self.i2c.registers[0x09])
        self.assertAlmostEqual(3.456, self.bq.get_ov_trip(), 1)

    def test_UV_TRIP(self):
        self.bq.setup()
        self.assertEqual(0b10100100, self.i2c.registers[0x0A])
        self.assertAlmostEqual(2.5, self.bq.get_uv_trip(), 1)

        self.bq.adc_gain = 380
        self.bq.adc_offset = 36
        self.bq.set_uv_trip(2.718)
        self.assertEqual(0b10111001, self.i2c.registers[0x0A])
        self.assertAlmostEqual(2.718, self.bq.get_uv_trip(), 1)

    def test_PROTECT1_SCD_values(self):
        self.bq.setup()

        protect1 = self.i2c.registers[0x06]
        rsns = (protect1 & 0b10000000) >> 7
        self.assertEqual(CONF.BQ_RSNS, rsns)

        scd_delay = (protect1 & 0b00011000) >> 3
        self.assertEqual(CONF.BQ_SCD_DELAY, scd_delay)

        scd_thresh = protect1 & 0b00000111
        self.assertEqual(CONF.BQ_SCD_THRESH, scd_thresh)

    def test_PROTECT2_OCD_values(self):
        self.bq.setup()

        protect2 = self.i2c.registers[0x07]
        ocd_delay = (protect2 & 0b1110000) >> 4
        self.assertEqual(CONF.BQ_OCD_DELAY, ocd_delay)

        ocd_thresh = (protect2 & 0b1111)
        self.assertEqual(CONF.BQ_OCD_THRESH, ocd_thresh)

    def test_PROTECT3_UV_OV_delays(self):
        self.bq.setup()

        protect3 = self.i2c.registers[0x08]
        uv_delay = (protect3 & 0b11000000) >> 6
        ov_delay = (protect3 & 0b00110000) >> 4
        self.assertEqual(CONF.BQ_UV_DELAY, uv_delay)
        self.assertEqual(CONF.BQ_OV_DELAY, ov_delay)

    def test_process_alert_with_cc_ready(self):
        self.i2c.registers[0x0] = 0b10000000
        self.i2c.registers[0x32] = 0x7D
        self.i2c.registers[0x33] = 0x0
        self.bq.process_alert()

        self.assertEqual(0b10000000, self.i2c.registers[0x0])
        self.assertEqual([], self.bq.faults)
        self.assertAlmostEqual(270.1, self.bq.amperage, 1)
        
    def test_process_alert_faults(self):
        self.i2c.registers[0x32] = 0
        self.i2c.registers[0x33] = 0
        self.i2c.registers[0x0] = 0b00000000
        self.bq.process_alert()
        self.assertEqual([], self.bq.faults)

        self.i2c.registers[0x0] = 0b10111111
        self.bq.process_alert()
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

        self.bq.clear_fault(DEVICE_XREADY)
        self.assertEqual(0b00100000, self.i2c.registers[0x0])
        self.assertEqual([], self.bq.faults)
        
    def test_load_cell_voltages_15(self):
        self.bq.setup()

        cells = Cells(15)
        self.bq.load_cell_voltages(cells)

        self.assertAlmostEqual(2.7, cells[0].voltage, 1)
        self.assertAlmostEqual(2.8, cells[1].voltage, 1)
        self.assertAlmostEqual(2.9, cells[2].voltage, 1)
        self.assertAlmostEqual(3.0, cells[3].voltage, 1)
        self.assertAlmostEqual(3.1, cells[4].voltage, 1)
        self.assertAlmostEqual(3.2, cells[5].voltage, 1)
        self.assertAlmostEqual(3.3, cells[6].voltage, 1)
        self.assertAlmostEqual(3.4, cells[7].voltage, 1)
        self.assertAlmostEqual(3.5, cells[8].voltage, 1)
        self.assertAlmostEqual(3.6, cells[9].voltage, 1)
        self.assertAlmostEqual(3.7, cells[10].voltage, 1)
        self.assertAlmostEqual(3.8, cells[11].voltage, 1)
        self.assertAlmostEqual(3.9, cells[12].voltage, 1)
        self.assertAlmostEqual(4.0, cells[13].voltage, 1)
        self.assertAlmostEqual(4.1, cells[14].voltage, 1)

    def test_load_cell_voltages_9(self):
        self.bq.setup()
        cells = Cells(9)
        self.bq.load_cell_voltages(cells)

        self.assertAlmostEqual(2.7, cells[0].voltage, 1)
        self.assertAlmostEqual(2.8, cells[1].voltage, 1)
        self.assertAlmostEqual(3.1, cells[2].voltage, 1)
        self.assertAlmostEqual(3.2, cells[3].voltage, 1)
        self.assertAlmostEqual(3.3, cells[4].voltage, 1)
        self.assertAlmostEqual(3.6, cells[5].voltage, 1)
        self.assertAlmostEqual(3.7, cells[6].voltage, 1)
        self.assertAlmostEqual(3.8, cells[7].voltage, 1)
        self.assertAlmostEqual(4.1, cells[8].voltage, 1)

    def test_batt_voltage(self):
        self.bq.adc_gain = 377
        self.bq.adc_offset = 45
        self.i2c.registers[0x2A] = 97
        self.i2c.registers[0x2B] = 215

        self.assertEqual(10, CONF.CELL_COUNT) # otherwise calculation doesn't work
        self.assertAlmostEqual(38.227, self.bq.batt_voltage(), 1)
        
    def test_setting_cells_to_balance(self):
        for id in [1, 3, 5, 6, 8, 10, 11, 13, 15]:
            self.bq.set_balance_cell(id, True)
        self.assertEqual(0b00010101, self.i2c.registers[0x01])
        self.assertEqual(0b00010101, self.i2c.registers[0x02])
        self.assertEqual(0b00010101, self.i2c.registers[0x03])

        for id in [2, 4, 7, 9, 12, 14]:
            self.bq.set_balance_cell(id, True)
        self.assertEqual(0b00011111, self.i2c.registers[0x01])
        self.assertEqual(0b00011111, self.i2c.registers[0x02])
        self.assertEqual(0b00011111, self.i2c.registers[0x03])

        for id in [1, 3, 5, 6, 8, 10, 11, 13, 15]:
            self.bq.set_balance_cell(id, False)
        self.assertEqual(0b00001010, self.i2c.registers[0x01])
        self.assertEqual(0b00001010, self.i2c.registers[0x02])
        self.assertEqual(0b00001010, self.i2c.registers[0x03])

    def test_is_cell_balancing(self):
        self.assertEqual(False, self.bq.is_cell_balancing(1))
        self.assertEqual(False, self.bq.is_cell_balancing(2))
        self.assertEqual(False, self.bq.is_cell_balancing(3))

        self.bq.set_balance_cell(1, True)
        self.bq.set_balance_cell(3, True)

        self.assertEqual(True, self.bq.is_cell_balancing(1))
        self.assertEqual(False, self.bq.is_cell_balancing(2))
        self.assertEqual(True, self.bq.is_cell_balancing(3))
        
    def test_turn_off_balancing(self):
        for id in [1, 3, 5, 6, 8, 10, 11, 13, 15]:
            self.bq.set_balance_cell(id, True)

        self.bq.reset_balancing()

        self.assertEqual(0b00000000, self.i2c.registers[0x01])
        self.assertEqual(0b00000000, self.i2c.registers[0x02])
        self.assertEqual(0b00000000, self.i2c.registers[0x03])

    def test_setup_resets_balancing(self):
        self.bq.set_balance_cell(1, True)
        self.bq.set_balance_cell(6, True)
        self.bq.set_balance_cell(11, True)

        self.bq.setup()

        self.assertEqual(0b00000000, self.i2c.registers[0x01])
        self.assertEqual(0b00000000, self.i2c.registers[0x02])
        self.assertEqual(0b00000000, self.i2c.registers[0x03])

    def test_discharge_setting(self):
        self.assertEqual(0x05, DSG_ON >> 8)
        self.assertEqual(1 << 1, DSG_ON & 255)

    def test_charge_setting(self):
        self.assertEqual(0x05, CHG_ON >> 8)
        self.assertEqual(1, CHG_ON & 255)
        
    def test_setup_disables_CHG_and_DSG(self):
        self.i2c.registers[0x05] = 255
        self.bq.setup()
        self.assertEqual(False, self.bq.get_reg_bit(DSG_ON))
        self.assertEqual(False, self.bq.get_reg_bit(CHG_ON))

    def test_clear_sys_stat(self):
        self.bq.clear_sys_stat()
        self.assertEqual(0xBF, self.i2c.registers[0x0])

    def test_clears_sys_stat_on_setup(self):
        self.bq.setup()
        self.assertEqual(0xBF, self.i2c.registers[0x0])

    def test_reading_amperage(self):
        self.i2c.registers[0x32] = 0
        self.i2c.registers[0x33] = 0
        self.bq.load_amperage()
        self.assertAlmostEqual(0, self.bq.amperage, 1)

        self.i2c.registers[0x32] = 0x7D
        self.i2c.registers[0x33] = 0x0
        self.bq.load_amperage()
        self.assertAlmostEqual(270.1, self.bq.amperage, 1)

        self.i2c.registers[0x32] = 0x83
        self.i2c.registers[0x33] = 0x0
        self.bq.load_amperage()
        self.assertAlmostEqual(-270.1, self.bq.amperage, 1)

        self.i2c.registers[0x32] = 0xFF
        self.i2c.registers[0x33] = 0xFF
        self.bq.load_amperage()
        self.assertAlmostEqual(0, self.bq.amperage, 1)

    def test_process_alert_with_cc_ready(self):
        self.i2c.registers[0x0] = 0b10000000
        self.i2c.registers[0x32] = 0x7D
        self.i2c.registers[0x33] = 0x0
        self.bq.process_alert()

        self.assertEqual(0b10000000, self.i2c.registers[0x0])
        self.assertEqual([], self.bq.faults)
        self.assertAlmostEqual(270.1, self.bq.amperage, 1)


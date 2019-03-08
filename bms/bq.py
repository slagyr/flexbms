from bms.conf import *

I2C_ADDR = 0x08
CRC_KEY = 7

# Registers
SYS_STAT = 0x00
CELLBAL1 = 0x01
CELLBAL2 = 0x02
CELLBAL3 = 0x03
SYS_CTRL1 = 0x04
SYS_CTRL2 = 0x05
PROTECT1 = 0x06
PROTECT2 = 0x07
PROTECT3 = 0x08
OV_TRIP = 0x09
UV_TRIP = 0x0A
CC_CFG = 0x0B
VC1_HI = 0x0C
BAT_HI = 0x2A
TS1_HI = 0x2C
TS1_LO = 0x2D
CC_HI = 0x32
CC_LO = 0x33
ADCGAIN1 = 0x50
ADCOFFSET = 0x51
ADCGAIN2 = 0x59

# Combined register address and bit mask, used in get|set_reg_bit
# 16 bits used, left 8 -> register, right 8 -> bit mask
#
#    register   mask
# 0b 00000000 00000000
#
CC_READY = (SYS_STAT << 8) | (1 << 7)
DEVICE_XREADY = (SYS_STAT << 8) | (1 << 5)
OVRD_ALERT = (SYS_STAT << 8) | (1 << 4)
UV = (SYS_STAT << 8) | (1 << 3)
OV = (SYS_STAT << 8) | (1 << 2)
SCD = (SYS_STAT << 8) | (1 << 1)
OCD = (SYS_STAT << 8) | (1 << 0)
ADC_EN = (SYS_CTRL1 << 8) | (1 << 4)
CC_EN = (SYS_CTRL2 << 8) | (1 << 6)

# Masks
LOAD_PRESENT = 1 << 7
TEMP_SEL = 1 << 3
SHUT_A = 1 << 1
SHUT_B = 1 << 0
DELAY_DIS = 1 << 7
CC_ONESHOT = 1 << 5
DSG_ON = 1 << 1
CHG_ON = 1 << 0


def crc8(data):
    crc = 0
    for i in range(len(data)):
        factor = 0x80
        while factor != 0:
            if crc & 0x80 != 0:
                crc = (crc * 2) & 0xFF
                crc ^= CRC_KEY
            else:
                crc = (crc * 2) & 0xFF
            if data[i] & factor != 0:
                crc ^= CRC_KEY
            factor = int(factor / 2)
    return crc


class BQ:
    def __init__(self, i2c):
        self.i2c = i2c
        self.adc_gain = -1
        self.adc_offset = -1
        self.cc_ready = False
        self.faults = []

    def __enter__(self):
        while not self.i2c.try_lock():
            pass
        return self.i2c

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.i2c.unlock()
        return False

    def read_register(self, reg, buffer):
        with self as i2c:
            i2c.writeto(I2C_ADDR, bytearray([reg]))
            i2c.readfrom_into(I2C_ADDR, buffer)
        return buffer

    def read_register_single(self, reg):
        for attempt in range(BQ_CRC_ATTEMPTS):
            buffer = self.read_register(reg, bytearray(2))
            crc = crc8(bytearray([17, buffer[0]]))
            if buffer[1] != crc:
                print("CRC failed.  attempt: " + str(attempt + 1))
                print("\texpected: " + str(crc) + " got: " + str(buffer[1]))
                print("\tregister: " + hex(reg) + " data: " + str(list(buffer)))
            else:
                break
        return buffer[0]

    def read_register_double(self, reg):
        for attempt in range(BQ_CRC_ATTEMPTS):
            buffer = self.read_register(reg, bytearray(4))
            crc1 = crc8(bytearray([17, buffer[0]]))
            crc2 = crc8(bytearray([buffer[2]]))
            if crc1 != buffer[1] or crc2 != buffer[3]:
                print("CRC failed.  attempt: " + str(attempt + 1))
                print("\texpected: " + str([crc1, crc2]) + " got: " + str([buffer[1], buffer[3]]))
                print("\tregister: " + hex(reg) + " data: " + str(list(buffer)))
        return (buffer[0] << 8) | buffer[2]

    def write_register(self, reg, byte):
        crc = crc8(bytearray([16, reg, byte]))
        with self as i2c:
            i2c.writeto(I2C_ADDR, bytearray([reg, byte, crc]))

    def set_reg_bit(self, reg_n_mask, enable):
        reg = reg_n_mask >> 8
        mask = reg_n_mask & 0xFF
        reg_val = self.read_register_single(reg)
        adc_en = reg_val & mask
        if bool(enable) != bool(adc_en):
            if enable:
                reg_val |= mask
            else:
                reg_val ^= mask
        self.write_register(reg, reg_val)

    def get_reg_bit(self, reg_n_mask):
        reg = reg_n_mask >> 8
        mask = reg_n_mask & 0xFF
        reg_val = self.read_register_single(reg)
        return bool(reg_val & mask)

    def read_adc_gain(self):
        gain1 = self.read_register_single(ADCGAIN1)
        gain2 = self.read_register_single(ADCGAIN2)
        gain_raw = (gain1 & 0b00001100) << 1 | (gain2 & 0b11100000) >> 5
        return 365 + gain_raw

    def read_adc_offset(self):
        offset = self.read_register_single(ADCOFFSET)
        if offset > 127:
            return -256 + offset
        else:
            return offset

    def adc_to_v(self, adc):
        return (self.adc_gain / 1000 * adc + self.adc_offset) / 1000

    def v_to_adc(self, v):
        return int(1000 * (1000 * v - self.adc_offset) / self.adc_gain)

    def set_ov_trip(self, v):
        if v < 3.15 or v > 4.7:
            raise RuntimeError("OV TRIP voltage out of range: " + str(v))
        adc = self.v_to_adc(v)
        ov_trip = (adc >> 4) & 0xFF
        self.write_register(OV_TRIP, ov_trip)

    def get_ov_trip(self):
        ov_trip = self.read_register_single(OV_TRIP)
        adc = (ov_trip << 4) | 0b10000000001000
        return self.adc_to_v(adc)

    def set_uv_trip(self, v):
        if v < 1.58 or v > 3.1:
            raise RuntimeError("UV TRIP voltage out of range: " + str(v))
        adc = self.v_to_adc(v)
        uv_trip = (adc >> 4) & 0xFF
        self.write_register(UV_TRIP, uv_trip)

    def get_uv_trip(self):
        uv_trip = self.read_register_single(UV_TRIP)
        adc = (uv_trip << 4) | 0b01000000000000
        return self.adc_to_v(adc)

    def set_protect1(self, rsns, scd_delay, scd_thresh):
        protect1 = (rsns & 0b1) << 7
        protect1 |= (scd_delay & 0b11) << 3
        protect1 |= scd_thresh & 0b111
        self.write_register(PROTECT1, protect1)

    def set_protect2(self, ocd_delay, ocd_thresh):
        protect2 = (ocd_delay & 0b111) << 4
        protect2 |= ocd_thresh & 0b1111
        self.write_register(PROTECT2, protect2)

    def set_protect3(self, uv_delay, ov_delay):
        protect3 = (uv_delay & 0b11) << 6
        protect3 |= (ov_delay & 0b11) << 4
        self.write_register(PROTECT3, protect3)

    def check_sys_stat(self):
        stat = self.read_register_single(SYS_STAT)
        self.cc_ready = stat & (CC_READY & 0xFF)
        if stat & (DEVICE_XREADY & 0xFF):
            if stat & (OVRD_ALERT & 0xFF):
                self.faults.append(OVRD_ALERT)
            if stat & (UV & 0xFF):
                self.faults.append(UV)
            if stat & (OV & 0xFF):
                self.faults.append(OV)
            if stat & (SCD & 0xFF):
                self.faults.append(SCD)
            if stat & (OCD & 0xFF):
                self.faults.append(OCD)
        else:
            assert stat & 0b00111111 == 0

    def clear_fault(self, fault):
        stat = (DEVICE_XREADY & 0xFF)
        stat |= (fault & 0xFF)
        self.write_register(SYS_STAT, stat)
        if fault != DEVICE_XREADY:
            self.faults.remove(fault)

    def setup(self):
        with self as i2c:
            if I2C_ADDR not in i2c.scan():
                raise RuntimeError("BQ address not found in scan")

        self.write_register(CC_CFG, 0x19)
        self.set_reg_bit(ADC_EN, True)
        self.set_reg_bit(CC_EN, True)
        self.adc_gain = self.read_adc_gain()
        self.adc_offset = self.read_adc_offset()
        self.set_ov_trip(CELL_MAX_V)
        self.set_uv_trip(CELL_MIN_V)
        self.set_protect1(BQ_RSNS, BQ_SCD_DELAY, BQ_SCD_THRESH)
        self.set_protect2(BQ_OCD_DELAY, BQ_OCD_THRESH)
        self.set_protect3(BQ_UV_DELAY, BQ_OV_DELAY)

        # TODO - verify ADC enabled
        # TODO - verify CC enabled
        # TODO - verify UV trip
        # TODO - verify OV trip
        # TODO - verify RSNS
        # TODO - verify SCD_DELAY
        # TODO - verify SCD_THRESH
        # TODO - verify OCD_DELAY
        # TODO - verify OCD_THRESH
        # TODO - ensure DEVICE_XREADY
        # print("GAIN: " + str(self.adc_gain))
        # print("OFFSET: " + str(self.adc_offset))
        # print("ADC_EN: " + str(self.get_reg_bit(ADC_EN)))
        # print("CC_EN: " + str(self.get_reg_bit(CC_EN)))
        # print("UV trip: " + str(self.get_uv_trip()))
        # print("OV trip: " + str(self.get_ov_trip()))
        # print("PROTECT1: " + str(self.read_register_single(PROTECT1)))
        # print("PROTECT2: " + str(self.read_register_single(PROTECT2)))
        # print("FAULTS: " + str(self.faults))

    def cell_voltage(self, cell_id):
        reg = VC1_HI + 2 * (cell_id - 1)
        adc = self.read_register_double(reg) & 0b0011111111111111
        return self.adc_to_v(adc)

    def batt_voltage(self):
        adc = self.read_register_double(BAT_HI)
        return ((adc * 4 * self.adc_gain / 1000) + (self.adc_offset * CELL_COUNT)) / 1000

    def set_balance_cell(self, id, on):
        if id < 1 or id > 15:
            raise RuntimeError("Invalid cell id: " + str(id))
        reg = CELLBAL1 + int((id-1) / 5)
        mask = 1 << ((id-1) % 5)
        cellbal = self.read_register_single(reg)
        if bool(cellbal & mask) != bool(on):
            if on:
                cellbal |= mask
            else:
                cellbal ^= mask
            self.write_register(reg, cellbal)

    def is_cell_balancing(self, id):
        if id < 1 or id > 15:
            raise RuntimeError("Invalid cell id: " + str(id))
        reg = CELLBAL1 + int((id-1) / 5)
        mask = 1 << ((id-1) % 5)
        cellbal = self.read_register_single(reg)
        return bool(cellbal & mask)

    def set_balance_cells(self, cell_ids):
        for id in range(1, 16):
            if id in cell_ids:
                self.set_balance_cell(id, True)
            else:
                self.set_balance_cell(id, False)


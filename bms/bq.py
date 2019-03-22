from bms.conf import *
from bms.util import clocked_fn, ON_BOARD, log

if not ON_BOARD:
    from bms.util import const

I2C_ADDR = const(0x08)
CRC_KEY = 7

# Registers
SYS_STAT = const(0x00)
CELLBAL1 = const(0x01)
CELLBAL2 = const(0x02)
CELLBAL3 = const(0x03)
SYS_CTRL1 = const(0x04)
SYS_CTRL2 = const(0x05)
PROTECT1 = const(0x06)
PROTECT2 = const(0x07)
PROTECT3 = const(0x08)
OV_TRIP = const(0x09)
UV_TRIP = const(0x0A)
CC_CFG = const(0x0B)
VC1_HI = const(0x0C)
BAT_HI = const(0x2A)
TS1_HI = const(0x2C)
# TS1_LO = const(0x2D)
CC_HI = const(0x32)
# CC_LO = const(0x33)
ADCGAIN1 = const(0x50)
ADCOFFSET = const(0x51)
ADCGAIN2 = const(0x59)

# Combined register address and bit mask, used in get|set_reg_bit
# 16 bits used, left 8 -> register, right 8 -> bit mask
#
#    register   mask
# 0b 00000000 00000000
#
CC_READY = const((SYS_STAT << 8) | (1 << 7))
DEVICE_XREADY = const((SYS_STAT << 8) | (1 << 5))
OVRD_ALERT = const((SYS_STAT << 8) | (1 << 4))
UV = const((SYS_STAT << 8) | (1 << 3))
OV = const((SYS_STAT << 8) | (1 << 2))
SCD = const((SYS_STAT << 8) | (1 << 1))
OCD = const((SYS_STAT << 8) | (1 << 0))
LOAD_PRESENT = const((SYS_CTRL1 << 8) | (1 << 7))  # Don't think it applies to FelxBMS v1.1 PCB
ADC_EN = const((SYS_CTRL1 << 8) | (1 << 4))
TEMP_SEL = const((SYS_CTRL1 << 8) | (1 << 3))
SHUT_A = const((SYS_CTRL1 << 8) | (1 << 1))
SHUT_B = const((SYS_CTRL1 << 8) | (1 << 0))
DELAY_DIS = const((SYS_CTRL2 << 8) | (1 << 7))
CC_EN = const((SYS_CTRL2 << 8) | (1 << 6))
CC_ONESHOT = const((SYS_CTRL2 << 8) | (1 << 5))
DSG_ON = const((SYS_CTRL2 << 8) | (1 << 1))
CHG_ON = const((SYS_CTRL2 << 8) | (1 << 0))


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
        self.faults = []
        self.amperage = 0

    def read_register(self, reg, buffer):
        i2c = self.i2c
        i2c.send(bytearray([reg]), I2C_ADDR)
        i2c.recv(buffer, I2C_ADDR)
        return buffer

    def read_register_single(self, reg):
        for attempt in range(BQ_CRC_ATTEMPTS):
            buffer = self.read_register(reg, bytearray([0, 0]))
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
        self.i2c.send(bytearray([reg, byte, crc]), I2C_ADDR)

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

    def adc_to_v(self, adc):
        return (self.adc_gain / 1000 * adc + self.adc_offset) / 1000

    def v_to_adc(self, v):
        return int(1000 * (1000 * v - self.adc_offset) / self.adc_gain)

    def setup(self):
        # with self as i2c:
        if I2C_ADDR not in self.i2c.scan():
            raise RuntimeError("BQ address not found in scan")

        self.write_register(CC_CFG, 0x19)
        self.adc_gain = self.read_adc_gain()
        self.adc_offset = self.read_adc_offset()
        self.set_ov_trip(CELL_MAX_V)
        self.set_uv_trip(CELL_MIN_V)
        self.set_protect1(BQ_RSNS, BQ_SCD_DELAY, BQ_SCD_THRESH)
        self.set_protect2(BQ_OCD_DELAY, BQ_OCD_THRESH)
        self.set_protect3(BQ_UV_DELAY, BQ_OV_DELAY)
        self.reset_balancing()
        self.discharge(False)
        self.charge(False)
        self.adc(False)
        self.cc(False)
        self.clear_sys_stat()

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

    def clear_fault(self, fault):
        stat = (DEVICE_XREADY & 0xFF)
        stat |= (fault & 0xFF)
        self.write_register(SYS_STAT, stat)
        if fault != DEVICE_XREADY:
            self.faults.remove(fault)

    def process_alert(self):
        stat = self.read_register_single(SYS_STAT)
        if stat & (CC_READY & 0xFF):
            self.load_amperage()
            self.set_reg_bit(CC_READY, True)
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
            if stat & 0b00111111 != 0:
                log("bq.sys_stat: unusual end status: " + str(stat))

    def clear_sys_stat(self):
        self.write_register(SYS_STAT, 0xBF)

    def cell_voltage(self, cell_id):
        reg = VC1_HI + 2 * (cell_id - 1)
        adc = self.read_register_double(reg) & 0b0011111111111111
        return self.adc_to_v(adc)

    def load_cell_voltages(self, cells):
        buf = self.read_register(VC1_HI, bytearray(60))
        crc = crc8(bytearray([17, buf[0]]))
        if crc != buf[1]:
            print("CRC failed on cell_voltages byte 0")
        for i in range(1, 30):
            i2 = i * 2
            crc = crc8(buf[i2:i2 + 1])
            if crc != buf[i2 + 1]:
                print("CRC failed on cell_voltages byte " + str(i) + ". got: " + str(buf[i + 1]) + " expected: " + str(
                    crc))

        adc_to_v = self.adc_to_v
        for cell in cells:
            i = (cell.id - 1) * 4
            reg_val = (buf[i] << 8) + buf[i + 2]
            adc = reg_val & 0b0011111111111111
            cell.voltage = adc_to_v(adc)

    def batt_voltage(self):
        adc = self.read_register_double(BAT_HI)
        return ((adc * 4 * self.adc_gain / 1000) + (self.adc_offset * CELL_COUNT)) / 1000

    def set_balance_cell(self, id, on):
        if id < 1 or id > 15:
            raise RuntimeError("Invalid cell id: " + str(id))
        reg = CELLBAL1 + int((id - 1) / 5)
        mask = 1 << ((id - 1) % 5)
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
        reg = CELLBAL1 + int((id - 1) / 5)
        mask = 1 << ((id - 1) % 5)
        cellbal = self.read_register_single(reg)
        return bool(cellbal & mask)

    def reset_balancing(self):
        self.write_register(CELLBAL1, 0)
        self.write_register(CELLBAL2, 0)
        self.write_register(CELLBAL3, 0)

    def load_amperage(self):
        lsb = 8.44  # uV
        sense_r = 0.001
        adc = self.read_register_double(CC_HI)
        if adc > 32767:  # Two's compliment
            adc = -65536 + adc
        v = adc * (lsb / 1000000)
        a = v / sense_r
        print("adc:", adc, "v:", v, "a:", a)
        self.amperage = a

    def discharge(self, on=None):
        if on is None:
            return self.get_reg_bit(DSG_ON)
        else:
            self.set_reg_bit(DSG_ON, on)

    def charge(self, on=None):
        if on is None:
            return self.get_reg_bit(CHG_ON)
        else:
            self.set_reg_bit(CHG_ON, on)

    def adc(self, on=None):
        if on is None:
            return self.get_reg_bit(ADC_EN)
        else:
            self.set_reg_bit(ADC_EN, on)

    def cc(self, on=None):
        if on is None:
            return self.get_reg_bit(CC_EN)
        else:
            self.set_reg_bit(CC_EN, on)

    def cc_oneshot(self):
        self.set_reg_bit(CC_ONESHOT, True)

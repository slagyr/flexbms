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
U_TRIP = 0x0A
CC_CFG = 0x0B
VC1_HI = 0x0C
VC1_LO = 0x0D
BAT_HI = 0x2A
BAT_LO = 0x2B
TS1_HI = 0x2C
TS1_LO = 0x2D
CC_HI = 0x32
CC_LO = 0x33
ADCGAIN1 = 0x50
ADCOFFSET = 0x51
ADCGAIN2 = 0x59

# Combined register address and bit mask
# 16 bits used, left 8 -> register, right 8 -> bit mask
#
#    register   mask
# 0b 00000000 00000000
#
ADC_EN = (SYS_CTRL1 << 8) | (1 << 4)
CC_EN = (SYS_CTRL2 << 8) | (1 << 6)

# Masks
CC_READY = 1 << 7
DEVICE_XREADY = 1 << 5
OVRD_ALERT = 1 << 4
UV = 1 << 3
OV = 1 << 2
SCD = 1 << 1
OCD = 1 << 0
LOAD_PRESENT = 1 << 7
TEMP_SEL = 1 << 3
SHUT_A = 1 << 1
SHUT_B = 1 << 0
DELAY_DIS = 1 << 7
CC_ONESHOT = 1 << 5
DSG_ON = 1 << 1
CHG_ON = 1 << 0


class BQ76940:
    def __init__(self, i2c):
        self.i2c = i2c

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
        buffer = self.read_register(reg, bytearray(1))
        return buffer[0]

    def read_register_double(self, reg):
        buffer = self.read_register(reg, bytearray(2))
        return (buffer[0] << 8) + buffer[1]

    def crc8(self, data):
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

    def write_register(self, reg, byte):
        crc = self.crc8(bytearray([16, reg, byte]))
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

    def setup(self):
        if I2C_ADDR not in self.i2c.scan():
            raise RuntimeError("BQ address not found in scan")

        self.write_register(CC_CFG, 0x19)
        self.set_reg_bit(ADC_EN, True)
        self.set_reg_bit(CC_EN, True)
        self.adc_gain = self.read_adc_gain()
        self.adc_offset = self.read_adc_offset()
        # TODO - set UV trip
        # TODO - set OV trip
        # TODO - write to PROTECT1
        # TODO - write to PROTECT2

        # TODO - verify ADC enabled
        # TODO - verify UV trip
        # TODO - verify OV trip
        # TODO - verify RSNS
        # TODO - verify SCD_DELAY
        # TODO - verify SCD_THRESH
        # TODO - verify OCD_DELAY
        # TODO - verify OCD_THRESH
        # TODO - ensure DEVICE_XREADY

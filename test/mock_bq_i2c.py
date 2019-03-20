from bms.bq import crc8

class MockBqI2C:
    def __init__(self):
        self.locked = False
        self.lock_count = 0
        self.registers = {}
        self.read_register = None
        self.scan_result = []
        self.scan_result = [0x08] # BQ76940 I@C Address
        self.registers[0x00] = 0b00000000 # SYS_STAT
        self.registers[0x01] = 0b00000000 # CELLBAL1
        self.registers[0x02] = 0b00000000 # CELLBAL2
        self.registers[0x03] = 0b00000000 # CELLBAL2
        self.registers[0x04] = 0b00000000 # SYSCTRL1
        self.registers[0x05] = 0b00000000 # SYSCTRL2
        self.registers[0x06] = 0b00000000 # PROTECT1
        self.registers[0x07] = 0b00000000 # PROTECT2
        self.registers[0x08] = 0b00000000 # PROTECT3
        self.registers[0x09] = 0b00000000 # OV_TRIP
        self.registers[0x0A] = 0b00000000 # UV_TRIP
        self.registers[0x50] = 0b00000000 # ADCGAIN1
        self.registers[0x59] = 0b00000000 # ADCGAIN2
        self.registers[0x51] = 0b00101010 # ADCOFFSET (42)
        for i in range(15):
            adc = 7282 + (274 * i)
            reg = 0x0C + i * 2
            self.registers[reg] = adc >> 8          #VCx_HI
            self.registers[reg + 1] = adc & 0xFF    #VCx_LO

    # def try_lock(self):
    #     if self.locked:
    #         return False
    #     else:
    #         self.locked = True
    #         self.lock_count += 1
    #         return True
    #
    # def unlock(self):
    #     self.locked = False

    def scan(self):
        return self.scan_result

    def send(self, bytes, address, **kwargs):
        assert address == 0x08
        if len(bytes) == 1:
            self.read_register = bytes[0]
        elif len(bytes) == 3:
            self.registers[bytes[0]] = bytes[1]
        else:
            raise RuntimeError("Unhandled I2C write")

    def recv(self, buffer, address, **kwargs):
        assert address == 0x08
        if self.read_register is None:
            raise IOError("Read register was not set")
        b = self.registers[self.read_register]
        buffer[0] = b
        buffer[1] = crc8(bytearray([17, b]))
        for i in range(1, int(len(buffer) / 2)):
            b = self.registers[self.read_register + i]
            buffer[i * 2] = b
            buffer[i * 2 + 1] = crc8(bytearray([b]))
        self.read_register = None

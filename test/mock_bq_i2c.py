from bms.bq import crc8

class MockBqI2C:
    def __init__(self):
        self.locked = False
        self.lock_count = 0
        self.registers = {}
        self.read_register = None
        self.scan_result = []

    def try_lock(self):
        if self.locked:
            return False
        else:
            self.locked = True
            self.lock_count += 1
            return True

    def unlock(self):
        self.locked = False

    def scan(self):
        return self.scan_result

    def writeto(self, address, bytes, **kwargs):
        assert address == 0x08
        if len(bytes) == 1:
            self.read_register = bytes[0]
        elif len(bytes) == 3:
            self.registers[bytes[0]] = bytes[1]
        else:
            raise RuntimeError("Unhandled I2C write")

    def readfrom_into(self, address, buffer, **kwargs):
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

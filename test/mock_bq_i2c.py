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
        if not self.read_register:
            raise IOError("Read register was not set: " + str(address))
        for i in range(len(buffer)):
            b = self.registers[self.read_register + i]
            buffer[i] = b
        self.read_register = None

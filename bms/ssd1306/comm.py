from adafruit_bus_device.i2c_device import I2CDevice

SSD1306_COMMAND =   0x00
SSD1306_DATA =      0x40

class Comm:
    def __init__(self, i2c):
        self.device = I2CDevice(i2c, 0x3C)
        self.inverted = False

    def setup(self):
        pass

    def cmd(self, command):
        with self.device as device:
            device.write(bytes([SSD1306_COMMAND, command]))

    def tx(self, data):
        if self.inverted:
            data = self.invert(data)
        with self.device as device:
            device.write(bytes([SSD1306_DATA]))
            device.write(data)

    def invert(self, data):
        size = len(data)
        inverted = bytearray(data)
        for i in range(0, size):
            inverted[i] = data[i] ^ 0xFF
        return inverted

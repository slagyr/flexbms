from adafruit_bus_device.i2c_device import I2CDevice

SSD1306_COMMAND =   0x00
SSD1306_DATA =      0x40

INVERSION = bytearray(256)
for i in range(0, 256):
    INVERSION[i] = i ^ 0xFF


class Comm:
    def __init__(self, i2c):
        self.device = I2CDevice(i2c, 0x3C)
        self.inverted = False

    def setup(self):
        pass

    def cmd(self, command):
        with self.device as device:
            device.write(bytes([SSD1306_COMMAND, command]), stop=True)

    def tx(self, data):
        if self.inverted:
            data = data.translate(INVERSION)
        with self.device as device:
            device.write(bytes([SSD1306_DATA]), stop=False)
            device.write(data, stop=True)

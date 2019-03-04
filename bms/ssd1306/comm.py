from adafruit_bus_device.i2c_device import I2CDevice

SSD1306_COMMAND =   0x00
SSD1306_DATA =      0x40

class Comm:
    def __init__(self, i2c):
        self.device = I2CDevice(i2c, 0x3C)

    def setup(self):
        pass

    def cmd(self, command):
        with self.device as device:
            device.write(bytes([SSD1306_COMMAND, command]))

    def tx(self, data):
        with self.device as device:
            device.write(bytes([SSD1306_DATA]))
            device.write(data)

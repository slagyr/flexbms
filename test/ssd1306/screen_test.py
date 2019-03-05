import unittest
from bms.ssd1306.screen import Screen
from mock_i2c import MockI2C
import bms.ssd1306.fonts as fonts
from bms.stream import ByteStream


class SSD1306Test(unittest.TestCase):

    def setUp(self):
        self.i2c = MockI2C()
        self.screen = Screen(self.i2c)
        self.commands = []
        self.datas = []

    def test_creation(self):
        self.assertIsInstance(self.screen, Screen)

    def check_writes(self):
        for write in self.i2c.writes:
            self.assertEqual(0x3C, write[0])
            if write[1][0] == 0x00:
                self.commands.append(write[1][1:])
            elif write[1][0] == 0x40:
                self.datas.append(write[1][1:])

    def test_setup(self):
        self.screen.setup()

        self.assertEqual(2, self.i2c.lock_count)
        self.check_writes()
        self.assertIn(bytearray([0xAE]), self.commands)  # display off
        self.assertIn(bytearray([0xA6]), self.commands)  # normal display
        self.assertIn(bytearray([0xD5]), self.commands)  # set display clock divide ratio
        self.assertIn(bytearray([0x80]), self.commands)  # -> suggested= ratio 0x80
        self.assertIn(bytearray([0xA8]), self.commands)  # set multiplex ratio
        self.assertIn(bytearray([63]), self.commands)  # -> height of display
        self.assertIn(bytearray([0xD3]), self.commands)  # set display offset
        self.assertIn(bytearray([0x0]), self.commands)  # -> none
        self.assertIn(bytearray([0x40]), self.commands)  # set start line -> 0
        self.assertIn(bytearray([0x8D]), self.commands)  # set charge pump enabled
        self.assertIn(bytearray([0x14]), self.commands)  # -> 0x14 enable, 0x10 disable
        self.assertIn(bytearray([0x20]), self.commands)  # set memory addressing mode
        self.assertIn(bytearray([0x00]), self.commands)  # -> 0x00 horizontal, 0x10 page, 0x01 vertical
        self.assertIn(bytearray([0xA1]), self.commands)  # set segment remap(0xA0, 0xA1)
        self.assertIn(bytearray([0xC8]), self.commands)  # set COM output direction(0xC0 inc, 0xC8 dec)
        self.assertIn(bytearray([0xDA]), self.commands)  # set COM pins conf
        self.assertIn(bytearray([0x12]), self.commands)  # -> got me!?!?!
        self.assertIn(bytearray([0x81]), self.commands)  # set contrast
        self.assertIn(bytearray([0xCF]), self.commands)  # -> quite high
        self.assertIn(bytearray([0xd9]), self.commands)  # set pre - charge period( in DCLK units)
        self.assertIn(bytearray([0xF1]), self.commands)  # -> 0xF1 high power, 0x22 battery power
        self.assertIn(bytearray([0xDB]), self.commands)  # set Vcommh deselect level(regulator output)
        self.assertIn(bytearray([0x40]), self.commands)  # -> (0x40 : 0.89 x Vcc, 0x00: 0.65 x Vcc)
        self.assertIn(bytearray([0xA4]), self.commands)  # display on(0xA4 from RAM, 0xA force ON)
        self.assertIn(bytearray([0x2E]), self.commands)  # deactivate scroll
        self.assertIn(bytearray([0xAF]), self.commands)  # display on

    def test_setup_clears_screen(self):
        self.screen.setup()

        self.check_writes()
        self.assertIn(bytearray([0x21, 0, 127]), self.commands)
        self.assertIn(bytearray([0x22, 0, 7]), self.commands)

        byxel = 128 * 8  # a byxel is 8 pixels in a columns of a page
        while byxel > 0:
            byxel -= 1
            self.assertEqual(0, self.datas[0][byxel])

    def test_initial_font(self):
        self.screen.setup()

        self.assertEqual(fonts.font6x8(), self.screen.font)
        self.assertEqual(6, self.screen.font_width())

    def create_bmp(self, size):
        bmp = bytearray(size)
        i = 0
        while i < size:
            bmp[i] = 0x42
            i += 1
        return bmp

    def test_draw_full_screen(self):
        bmp = self.create_bmp(1024)
        self.screen.draw_byxels(0, 0, 128, 8, ByteStream(bmp))

        self.assertEqual(bmp, self.screen.buffer[1:])

    def test_draw_full_screen_inverted(self):
        bmp = self.create_bmp(1024)
        self.screen.inverted = True
        self.screen.draw_byxels(0, 0, 128, 8, ByteStream(bmp))

        for i in range(1024):
            self.assertEqual(0x42 ^ 0xFF, self.screen.buffer[i + 1])

    def test_clear(self):
        bmp = self.create_bmp(1024)
        self.screen.draw_byxels(0, 0, 128, 8, ByteStream(bmp))
        self.screen.clear()

        self.assertEqual(bytearray(1024), self.screen.buffer[1:])

    def test_clear_inverted(self):
        bmp = self.create_bmp(1024)
        self.screen.inverted = True
        self.screen.draw_byxels(0, 0, 128, 8, ByteStream(bmp))
        self.screen.clear()

        for i in range(1024):
            self.assertEqual(255, self.screen.buffer[i + 1])

    def test_draw_and_show_full_screen(self):
        bmp = self.create_bmp(1024)
        self.screen.draw_byxels(0, 0, 128, 8, ByteStream(bmp))
        self.screen.show()

        self.check_writes()
        self.assertEqual(bytearray([0x21, 0, 127]), self.commands[0])
        self.assertEqual(bytearray([0x22, 0, 7]), self.commands[1])

        self.assertEqual(1024, len(self.datas[0]))
        self.assertEqual(bmp, bytearray(self.datas[0]))

    def test_quarter_screen_byxels(self):
        byxels = self.create_bmp(256)
        self.screen.draw_byxels(32, 2, 64, 4, ByteStream(byxels))

        buffer = self.screen.buffer[1:]

        self.assertEqual(bytearray(128), buffer[0:128])
        self.assertEqual(bytearray(128), buffer[128:256])

        self.assertEqual(bytearray(32), buffer[256:288])
        self.assertEqual(byxels[0:64], buffer[288:352])
        self.assertEqual(bytearray(32), buffer[352:384])

        self.assertEqual(bytearray(32), buffer[384:416])
        self.assertEqual(byxels[0:64], buffer[416:480])
        self.assertEqual(bytearray(32), buffer[480:512])

        self.assertEqual(bytearray(32), buffer[512:544])
        self.assertEqual(byxels[0:64], buffer[544:608])
        self.assertEqual(bytearray(32), buffer[608:640])

        self.assertEqual(bytearray(32), buffer[640:672])
        self.assertEqual(byxels[0:64], buffer[672:736])
        self.assertEqual(bytearray(32), buffer[736:768])

        self.assertEqual(bytearray(128), buffer[768:896])
        self.assertEqual(bytearray(128), buffer[896:1024])

    def test_set_font(self):
        self.screen.set_font(fonts.font5x7())

        self.assertEqual(fonts.font5x7(), self.screen.font)
        self.assertEqual(5, self.screen.font_width())

    def test_write_string(self):
        self.screen.draw_text(42, 3, "Hello")

        buffer = self.screen.buffer[1:]

        # H
        self.assertEqual(0, buffer[426])
        self.assertEqual(0x7F, buffer[427])
        self.assertEqual(0x08, buffer[428])
        self.assertEqual(0x08, buffer[429])
        self.assertEqual(0x08, buffer[430])
        self.assertEqual(0x7F, buffer[431])
        # e
        self.assertEqual(0, buffer[432])
        self.assertEqual(0x38, buffer[433])
        self.assertEqual(0x54, buffer[434])
        self.assertEqual(0x54, buffer[435])
        self.assertEqual(0x54, buffer[436])
        self.assertEqual(0x18, buffer[437])

    def test_inverted_text(self):
        self.assertEqual(False, self.screen.inverted)
        self.screen.inverted = True
        self.assertEqual(True, self.screen.inverted)

        self.screen.draw_text(42, 3, "Hello")

        buffer = self.screen.buffer[1:]
        # H
        self.assertEqual(0xFF, buffer[426])
        self.assertEqual(0x80, buffer[427])
        self.assertEqual(0xF7, buffer[428])
        self.assertEqual(0xF7, buffer[429])
        self.assertEqual(0xF7, buffer[430])
        self.assertEqual(0x80, buffer[431])
        # e
        self.assertEqual(0xFF, buffer[432])
        self.assertEqual(0xC7, buffer[433])
        self.assertEqual(0xAB, buffer[434])
        self.assertEqual(0xAB, buffer[435])
        self.assertEqual(0xAB, buffer[436])
        self.assertEqual(0xE7, buffer[437])

    # def test_splash(self):
    #     splash = bin.load("splash")
    #     # self.screen.set_inverted(True)
    #     self.screen.draw_byxels(0, 0, 128, 8, ByteStream(splash))
    #
    #     self.screen.print_buffer()

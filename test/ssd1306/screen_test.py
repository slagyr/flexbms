import unittest
from bms.ssd1306.screen import Screen
from mock_ssd1306_comm import MockSSD1306Comm
import bms.ssd1306.fonts as fonts
import bms.bin as bin
from bms.stream import ByteStream, FileStream

class SSD1306Test(unittest.TestCase):

    def setUp(self):
        self.comm = MockSSD1306Comm()
        self.screen = Screen(self.comm)

    def test_creation(self):
        self.assertIsInstance(self.screen, Screen)
        self.assertIs(self.comm, self.screen.comm)

    def test_setup(self):
        self.screen.setup()

        self.assertTrue(self.comm.was_setup)
        self.assertIn(0xAE, self.comm.commands) # display off
        self.assertIn(0xA6, self.comm.commands)  # normal display
        self.assertIn(0xD5, self.comm.commands)  # set display clock divide ratio
        self.assertIn(0x80, self.comm.commands)  # -> suggested= ratio 0x80
        self.assertIn(0xA8, self.comm.commands)  # set multiplex ratio
        self.assertIn(63, self.comm.commands)    # -> height of display
        self.assertIn(0xD3, self.comm.commands)  # set display offset
        self.assertIn(0x0, self.comm.commands)   # -> none
        self.assertIn(0x40 | 0x0, self.comm.commands)    # set start line -> 0
        self.assertIn(0x8D, self.comm.commands)  # set charge pump enabled
        self.assertIn(0x14, self.comm.commands)  # -> 0x14 enable, 0x10 disable
        self.assertIn(0x20, self.comm.commands)  # set memory addressing mode
        self.assertIn(0x00, self.comm.commands)  # -> 0x00 horizontal, 0x10 page, 0x01 vertical
        self.assertIn(0xA1, self.comm.commands)  # set segment remap(0xA0, 0xA1)
        self.assertIn(0xC8, self.comm.commands)  # set COM output direction(0xC0 inc, 0xC8 dec)
        self.assertIn(0xDA, self.comm.commands)  # set COM pins conf
        self.assertIn(0x12, self.comm.commands)  # -> got me!?!?!
        self.assertIn(0x81, self.comm.commands)  # set contrast
        self.assertIn(0xCF, self.comm.commands)  # -> quite high
        self.assertIn(0xd9, self.comm.commands)  # set pre - charge period( in DCLK units)
        self.assertIn(0xF1, self.comm.commands)  # -> 0xF1 high power, 0x22 battery power
        self.assertIn(0xDB, self.comm.commands)  # set Vcommh deselect level(regulator output)
        self.assertIn(0x40, self.comm.commands)  # -> (0x40 : 0.89 x Vcc, 0x00: 0.65 x Vcc)
        self.assertIn(0xA4, self.comm.commands)  # display on(0xA4 from RAM, 0xA force ON)
        self.assertIn(0x2E, self.comm.commands)  # deactivate scroll
        self.assertIn(0xAF, self.comm.commands)  # display on

    def test_setup_clears_screen(self):
        self.screen.setup()

        self.assertIn(0x21, self.comm.commands) # set column address
        self.assertIn(0, self.comm.commands)    # start column
        self.assertIn(127, self.comm.commands)  # end column
        self.assertIn(0x22, self.comm.commands) # set page (row) address
        self.assertIn(0, self.comm.commands)    # start row
        self.assertIn(7, self.comm.commands)    # end row

        byxel = 128 * 8  # a byxel is 8 pixels in a columns of a page
        while byxel > 0:
            byxel -= 1
            self.assertEqual(0, self.comm.data[byxel])


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

        self.assertEqual(bmp, self.screen.buffer)

    def test_draw_full_screen_inverted(self):
        bmp = self.create_bmp(1024)
        self.screen.set_inverted(True)
        self.screen.draw_byxels(0, 0, 128, 8, ByteStream(bmp))

        for i in range(1024):
            self.assertEqual(0x42 ^ 0xFF, self.screen.buffer[i])

    def test_clear(self):
        bmp = self.create_bmp(1024)
        self.screen.draw_byxels(0, 0, 128, 8, ByteStream(bmp))
        self.screen.clear()

        self.assertEqual(bytearray(1024), self.screen.buffer)

    def test_clear_inverted(self):
        bmp = self.create_bmp(1024)
        self.screen.set_inverted(True)
        self.screen.draw_byxels(0, 0, 128, 8, ByteStream(bmp))
        self.screen.clear()

        for i in range(1024):
            self.assertEqual(255, self.screen.buffer[i])

    def test_draw_and_show_full_screen(self):
        bmp = self.create_bmp(1024)
        self.screen.draw_byxels(0, 0, 128, 8, ByteStream(bmp))
        self.screen.show()

        self.assertEqual(0x21, self.comm.commands[0])
        self.assertEqual(0, self.comm.commands[1])
        self.assertEqual(127, self.comm.commands[2])
        self.assertEqual(0x22, self.comm.commands[3])
        self.assertEqual(0, self.comm.commands[4])
        self.assertEqual(7, self.comm.commands[5])

        self.assertEqual(1024, len(self.comm.data))
        self.assertEqual(bmp, bytearray(self.comm.data))

    def test_quarter_screen_byxels(self):
        byxels = self.create_bmp(256)
        self.screen.draw_byxels(32, 2, 64, 4, ByteStream(byxels))

        self.assertEqual(bytearray(128), self.screen.buffer[0:128])
        self.assertEqual(bytearray(128), self.screen.buffer[128:256])

        self.assertEqual(bytearray(32), self.screen.buffer[256:288])
        self.assertEqual(byxels[0:64], self.screen.buffer[288:352])
        self.assertEqual(bytearray(32), self.screen.buffer[352:384])

        self.assertEqual(bytearray(32), self.screen.buffer[384:416])
        self.assertEqual(byxels[0:64], self.screen.buffer[416:480])
        self.assertEqual(bytearray(32), self.screen.buffer[480:512])

        self.assertEqual(bytearray(32), self.screen.buffer[512:544])
        self.assertEqual(byxels[0:64], self.screen.buffer[544:608])
        self.assertEqual(bytearray(32), self.screen.buffer[608:640])

        self.assertEqual(bytearray(32), self.screen.buffer[640:672])
        self.assertEqual(byxels[0:64], self.screen.buffer[672:736])
        self.assertEqual(bytearray(32), self.screen.buffer[736:768])

        self.assertEqual(bytearray(128), self.screen.buffer[768:896])
        self.assertEqual(bytearray(128), self.screen.buffer[896:1024])


    def test_set_font(self):
        self.screen.set_font(fonts.font5x7())

        self.assertEqual(fonts.font5x7(), self.screen.font)
        self.assertEqual(5, self.screen.font_width())

    def test_write_string(self):
        self.screen.draw_text(42, 3, "Hello")

        # H
        self.assertEqual(0,    self.screen.buffer[426])
        self.assertEqual(0x7F, self.screen.buffer[427])
        self.assertEqual(0x08, self.screen.buffer[428])
        self.assertEqual(0x08, self.screen.buffer[429])
        self.assertEqual(0x08, self.screen.buffer[430])
        self.assertEqual(0x7F, self.screen.buffer[431])
        # e
        self.assertEqual(0,    self.screen.buffer[432])
        self.assertEqual(0x38, self.screen.buffer[433])
        self.assertEqual(0x54, self.screen.buffer[434])
        self.assertEqual(0x54, self.screen.buffer[435])
        self.assertEqual(0x54, self.screen.buffer[436])
        self.assertEqual(0x18, self.screen.buffer[437])

    def test_inverted_text(self):
        self.assertEqual(False, self.screen.is_inverted())
        self.screen.set_inverted(True)
        self.assertEqual(True, self.screen.is_inverted())

        self.screen.draw_text(42, 3, "Hello")

        # H
        self.assertEqual(0xFF, self.screen.buffer[426])
        self.assertEqual(0x80, self.screen.buffer[427])
        self.assertEqual(0xF7, self.screen.buffer[428])
        self.assertEqual(0xF7, self.screen.buffer[429])
        self.assertEqual(0xF7, self.screen.buffer[430])
        self.assertEqual(0x80, self.screen.buffer[431])
        # e
        self.assertEqual(0xFF, self.screen.buffer[432])
        self.assertEqual(0xC7, self.screen.buffer[433])
        self.assertEqual(0xAB, self.screen.buffer[434])
        self.assertEqual(0xAB, self.screen.buffer[435])
        self.assertEqual(0xAB, self.screen.buffer[436])
        self.assertEqual(0xE7, self.screen.buffer[437])

    # def test_splash(self):
    #     splash = bin.load("splash")
    #     # self.screen.set_inverted(True)
    #     self.screen.draw_byxels(0, 0, 128, 8, ByteStream(splash))
    #
    #     self.screen.print_buffer()
import unittest
from bms.ssd1306.screen import Screen
from mock_ssd1306_comm import MockSSD1306Comm
import bms.ssd1306.fonts as fonts

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

    def test_full_screen_bitmap(self):
        bmp = self.create_bmp(1024)
        self.screen.draw_bitmap(0, 0, 128, 64, bmp)

        self.assertEqual(0x21, self.comm.commands[0])
        self.assertEqual(0, self.comm.commands[1])
        self.assertEqual(127, self.comm.commands[2])
        self.assertEqual(0x22, self.comm.commands[3])
        self.assertEqual(0, self.comm.commands[4])
        self.assertEqual(7, self.comm.commands[5])

        self.assertEqual(1024, len(self.comm.data))
        self.assertEqual(bmp, bytearray(self.comm.data))

    def test_quarter_screen_bitmap(self):
        bmp = self.create_bmp(256)
        self.screen.draw_bitmap(32, 2, 64, 32, bmp)

        self.assertEqual(0x21, self.comm.commands[0])
        self.assertEqual(32, self.comm.commands[1])
        self.assertEqual(95, self.comm.commands[2])
        self.assertEqual(0x22, self.comm.commands[3])
        self.assertEqual(2, self.comm.commands[4])
        self.assertEqual(5, self.comm.commands[5])

        self.assertEqual(256, len(self.comm.data))
        self.assertEqual(bmp, bytearray(self.comm.data))

    def test_set_font(self):
        self.screen.set_font(fonts.font5x7())

        self.assertEqual(fonts.font5x7(), self.screen.font)
        self.assertEqual(5, self.screen.font_width())

    def test_write_string(self):
        self.screen.draw_string(42, 3, "Hello")

        self.assertEqual(0x21, self.comm.commands.pop(0))
        self.assertEqual(42, self.comm.commands.pop(0))
        self.assertEqual(71, self.comm.commands.pop(0))
        self.assertEqual(0x22, self.comm.commands.pop(0))
        self.assertEqual(3, self.comm.commands.pop(0))
        self.assertEqual(3, self.comm.commands.pop(0))

        self.assertEqual(30, len(self.comm.data))
        # H
        self.assertEqual(0, self.comm.data.pop(0))
        self.assertEqual(0x7F, self.comm.data.pop(0))
        self.assertEqual(0x08, self.comm.data.pop(0))
        self.assertEqual(0x08, self.comm.data.pop(0))
        self.assertEqual(0x08, self.comm.data.pop(0))
        self.assertEqual(0x7F, self.comm.data.pop(0))
        # e
        self.assertEqual(0, self.comm.data.pop(0))
        self.assertEqual(0x38, self.comm.data.pop(0))
        self.assertEqual(0x54, self.comm.data.pop(0))
        self.assertEqual(0x54, self.comm.data.pop(0))
        self.assertEqual(0x54, self.comm.data.pop(0))
        self.assertEqual(0x18, self.comm.data.pop(0))

    def test_clear(self):
        self.screen.clear(12, 3, 24, 3)

        self.assertEqual(0x21, self.comm.commands.pop(0))
        self.assertEqual(12, self.comm.commands.pop(0))
        self.assertEqual(35, self.comm.commands.pop(0))
        self.assertEqual(0x22, self.comm.commands.pop(0))
        self.assertEqual(3, self.comm.commands.pop(0))
        self.assertEqual(5, self.comm.commands.pop(0))

        self.assertEqual(72, len(self.comm.data))
        for i in range(0, 72):
            self.assertEqual(0, self.comm.data.pop(0))

    def test_inverted_text(self):
        self.assertEqual(False, self.screen.is_inverted())
        self.screen.set_inverted(True)
        self.assertEqual(True, self.screen.is_inverted())

        self.screen.draw_string(42, 3, "Hello")

        self.assertEqual(0x21, self.comm.commands.pop(0))
        self.assertEqual(42, self.comm.commands.pop(0))
        self.assertEqual(71, self.comm.commands.pop(0))
        self.assertEqual(0x22, self.comm.commands.pop(0))
        self.assertEqual(3, self.comm.commands.pop(0))
        self.assertEqual(3, self.comm.commands.pop(0))

        self.assertEqual(30, len(self.comm.data))
        # H
        self.assertEqual(0xFF, self.comm.data.pop(0))
        self.assertEqual(0x80, self.comm.data.pop(0))
        self.assertEqual(0xF7, self.comm.data.pop(0))
        self.assertEqual(0xF7, self.comm.data.pop(0))
        self.assertEqual(0xF7, self.comm.data.pop(0))
        self.assertEqual(0x80, self.comm.data.pop(0))
        # e
        self.assertEqual(0xFF, self.comm.data.pop(0))
        self.assertEqual(0xC7, self.comm.data.pop(0))
        self.assertEqual(0xAB, self.comm.data.pop(0))
        self.assertEqual(0xAB, self.comm.data.pop(0))
        self.assertEqual(0xAB, self.comm.data.pop(0))
        self.assertEqual(0xE7, self.comm.data.pop(0))
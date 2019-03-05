import bms.ssd1306.fonts as fonts

FONT_META_OFFSET = 2
SSD1306_CMND = 0x00
SSD1306_DATA = 0x40
SSD1306_ADDR = 0x3C


class Screen:

    def __init__(self, i2c):
        self.i2c = i2c
        self.font = fonts.font6x8()
        self.buffer = bytearray(1025)
        self.buffer[0] = SSD1306_DATA
        self.inverted = False

    def __enter__(self):
        while not self.i2c.try_lock():
            pass
        return self.i2c

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.i2c.unlock()
        return False


    def setup(self):
        with self as comm:
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xAE]))  # display off
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xA6]))  # normal display
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xD5]))  # set display clock divide ratio
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x80]))  # -> suggested= ratio 0x80
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xA8]))  # set multiplex ratio
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 63  ]))    # -> height of display
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xD3]))  # set display offset
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x0 ]))   # -> none
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x40]))  # set start line -> 0
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x8D]))  # set charge pump enabled
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x14]))  # -> 0x14 enable, 0x10 disable
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x20]))  # set memory addressing mode
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x00]))  # -> 0x00 horizontal, 0x10 page, 0x01 vertical
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xA1]))  # set segment remap(0xA0, 0xA1)
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xC8]))  # set COM output direction(0xC0 inc, 0xC8 dec)
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xDA]))  # set COM pins conf
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x12]))  # -> got me!?!?!
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x81]))  # set contrast
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xCF]))  # -> quite high
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xd9]))  # set pre - charge period( in DCLK units)
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xF1]))  # -> 0xF1 high power, 0x22 battery power
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xDB]))  # set Vcommh deselect level(regulator output)
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x40]))  # -> (0x40 : 0.89 x Vcc, 0x00: 0.65 x Vcc)
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xA4]))  # display on(0xA4 from RAM, 0xA force ON)
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x2E]))  # deactivate scroll
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0xAF]))  # display on
        self.clear()
        self.show()

    def set_font(self, font):
        self.font = font

    def font_width(self):
        return self.font[0]

    def clear(self):
        b = 0
        if self.inverted:
            b = 0xFF
        for i in range(1024):
            self.buffer[i + 1] = b

    def show(self):
        with self as comm:
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x21, 0, 127]))
            comm.writeto(SSD1306_ADDR, bytearray([SSD1306_CMND, 0x22, 0, 7]))
            comm.writeto(SSD1306_ADDR, self.buffer)

    def draw_byxels(self, x, r, width, rows, byxels):
        if len(byxels) != width * rows:
            raise IndexError("byxel count doesn't match width and rows")
        byxel_i = 0
        for row in range(r, r + rows):
            i = 128 * row + x
            for col in range(width):
                b = byxels[byxel_i]
                self.buffer[i + 1] = self.invert(b) if self.inverted else b
                i += 1
                byxel_i += 1

    def draw_text(self, x, r, msg):
        l = len(msg)
        font_w = self.font_width()
        buff_i = 128 * r + x
        for i in range(0, l):
            c = ord(msg[i])
            start = (c - 32) * font_w + FONT_META_OFFSET
            for j in range(0, font_w):
                b = self.font[start + j]
                self.buffer[buff_i + 1] = self.invert(b) if self.inverted else b
                buff_i += 1

    def invert(self, byxel):
        return byxel ^ 0xFF

    def print_buffer(self):
        for page in range(8):
            y = 128 * page
            for row in range(8):
                line_no = page * 8 + row
                txt = str(line_no) + " "
                if line_no < 10:
                    txt = " " + txt
                mask = 1 << row
                for col in range(128):
                    if self.buffer[y + col] & mask:
                        txt += "*"
                    else:
                        txt += " "
                print(txt)





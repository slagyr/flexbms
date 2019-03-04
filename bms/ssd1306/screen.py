import bms.ssd1306.fonts as fonts

FONT_META_OFFSET = 2


class Screen:

    def __init__(self, comm):
        self.comm = comm
        self.font = fonts.font6x8()
        self.buffer = bytearray(1024)
        self.inverted = False


    def setup(self):
        self.comm.setup()
        self.comm.cmd(0xAE)  # display off
        self.comm.cmd(0xA6)  # normal display
        self.comm.cmd(0xD5)  # set display clock divide ratio
        self.comm.cmd(0x80)  # -> suggested= ratio 0x80
        self.comm.cmd(0xA8)  # set multiplex ratio
        self.comm.cmd(63)    # -> height of display
        self.comm.cmd(0xD3)  # set display offset
        self.comm.cmd(0x0)   # -> none
        self.comm.cmd(0x40)  # set start line -> 0
        self.comm.cmd(0x8D)  # set charge pump enabled
        self.comm.cmd(0x14)  # -> 0x14 enable, 0x10 disable
        self.comm.cmd(0x20)  # set memory addressing mode
        self.comm.cmd(0x00)  # -> 0x00 horizontal, 0x10 page, 0x01 vertical
        self.comm.cmd(0xA1)  # set segment remap(0xA0, 0xA1)
        self.comm.cmd(0xC8)  # set COM output direction(0xC0 inc, 0xC8 dec)
        self.comm.cmd(0xDA)  # set COM pins conf
        self.comm.cmd(0x12)  # -> got me!?!?!
        self.comm.cmd(0x81)  # set contrast
        self.comm.cmd(0xCF)  # -> quite high
        self.comm.cmd(0xd9)  # set pre - charge period( in DCLK units)
        self.comm.cmd(0xF1)  # -> 0xF1 high power, 0x22 battery power
        self.comm.cmd(0xDB)  # set Vcommh deselect level(regulator output)
        self.comm.cmd(0x40)  # -> (0x40 : 0.89 x Vcc, 0x00: 0.65 x Vcc)
        self.comm.cmd(0xA4)  # display on(0xA4 from RAM, 0xA force ON)
        self.comm.cmd(0x2E)  # deactivate scroll
        self.comm.cmd(0xAF)  # display on
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
            self.buffer[i] = b

    def prepare_update(self, startX, endX, startP, endP):
        self.comm.cmd(0x21)
        self.comm.cmd(startX)
        self.comm.cmd(endX)
        self.comm.cmd(0x22)
        self.comm.cmd(startP)
        self.comm.cmd(endP)

    def show(self):
        self.prepare_update(0, 127, 0, 7)
        self.comm.tx(self.buffer)

    def draw_byxels(self, x, r, width, rows, stream):
        if stream.size() != width * rows:
            raise IndexError("byxel count doesn't match width and rows")
        with stream as byxels:
            for row in range(r, r + rows):
                i = 128 * row + x
                for col in range(width):
                    self.buffer[i] = self.prep(byxels.next())
                    i += 1

    def draw_text(self, x, r, msg):
        l = len(msg)
        font_w = self.font_width()
        buff_i = 128 * r + x
        for i in range(0, l):
            c = ord(msg[i])
            start = (c - 32) * font_w + FONT_META_OFFSET
            for j in range(0, font_w):
                self.buffer[buff_i] = self.prep(self.font[start + j])
                buff_i += 1

    def set_inverted(self, value):
        self.inverted = value

    def is_inverted(self):
        return self.inverted

    def invert(self, byxel):
        return byxel ^ 0xFF

    def prep(self, byxel):
        if self.inverted:
            return self.invert(byxel)
        else:
            return byxel

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





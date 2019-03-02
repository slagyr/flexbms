import bms.ssd1306.fonts as fonts

FONT_META_OFFSET = 2


class Screen:

    def __init__(self, comm):
        self.comm = comm
        self.font = fonts.font6x8()

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
        self.comm.cmd(0x40 | 0x0)    # set start line -> 0
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
        self.clear_screen()

    def set_font(self, font):
        self.font = font

    def font_width(self):
        return self.font[0]

    def clear_screen(self):
        self.clear(0, 0, 128, 8)

    def clear(self, x, r, width, rows):
        self.prepare_update(x, x + width - 1, r, r + rows - 1)
        self.comm.tx(bytearray(width * rows))

    def prepare_update(self, startX, endX, startP, endP):
        self.comm.cmd(0x21)
        self.comm.cmd(startX)
        self.comm.cmd(endX)
        self.comm.cmd(0x22)
        self.comm.cmd(startP)
        self.comm.cmd(endP)

    def draw_bitmap(self, x, r, w, h, bmp):
        rows = int(h / 8)
        self.prepare_update(x, x + w - 1, r, r + rows - 1)
        self.comm.tx(bmp)

    def draw_string(self, x, r, msg):
        l = len(msg)
        font_w = self.font_width()
        self.prepare_update(x, x + l * font_w - 1, r, r)

        data = bytearray()
        for i in range(0, l):
            c = ord(msg[i])
            start = (c - 32) * font_w + FONT_META_OFFSET
            for j in range(0, font_w):
                data.append(self.font[start + j])

        self.comm.tx(data)


    def set_inverted(self, value):
        self.comm.inverted = value

    def is_inverted(self):
        return self.comm.inverted

# void Oled::drawCanvas(byte x, byte row, byte widthPx, byte heightPx, byte *bytes) {
#     prepareScreenUpdate(x, x + widthPx - 1, row, row + heightPx / 8 - 1);
#     comm->beginTransmission();
#     int bytesInScreen = widthPx * heightPx / 8;
#     for(int i = 0; i < bytesInScreen; i++) {
#         comm->includeByte(bytes[i]);
#     }
#     comm->endTransmission();
# }

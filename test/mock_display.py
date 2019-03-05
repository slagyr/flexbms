import bms.bin


class MockDisplay:
    def __init__(self):
        self.was_setup = False
        self.was_shown = False
        self.drawings = []
        self.font = bms.bin.load("font6x8")

    def setup(self):
        self.was_setup = True

    def draw_byxels(self, x, r, width, rows, byxels):
        self.drawings.append([x, r, width, rows, byxels])

    def draw_text(self, x, r, msg):
        self.drawings.append([x, r, msg])

    def show(self):
        self.was_shown = True

    def set_font(self, font):
        self.font = font

    def draw_hline(self, x, y, l):
        pass

    def draw_dashed_hline(self, x, y, l, on, off):
        pass

    def draw_vline(self, x, y, l):
        pass

    def draw_rect(self, x, y, w, h):
        pass

    def clear(self):
        pass

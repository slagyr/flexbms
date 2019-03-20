from bms import fonts


class ErrorScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 999999999
        self.trace_lines = None

    def enter(self):
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        display.clear()
        self.read_error()
        self.draw_all(display)

    def update(self):
        pass

    def read_error(self):
        try:
            with open("error.txt", "r") as f:
                lines = f.readlines()[-5:]
                lines.reverse()
                self.trace_lines = lines
        except OSError:
            pass

    def draw_all(self, display):
        display.draw_text(8 * 6, 0, "ERROR")
        if not self.trace_lines:
            display.draw_text(0, 3, "Could not read")
            display.draw_text(0, 4, "error.txt")
        else:
            r = 1
            line = None
            lines = self.trace_lines
            while r < 8 and (line or lines):
                if not line:
                    line = lines[0].strip()
                    lines = lines[1:]
                txt = line
                if len(txt) > 21:
                    txt = txt[:21]
                    line = line[21:]
                else:
                    line = None
                display.draw_text(0, r, txt)
                r += 1
        display.show()



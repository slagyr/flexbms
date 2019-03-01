class MockSSD1306Comm:
    def __init__(self):
        self.was_setup = False
        self.commands = []
        self.data = []
        self.in_transmission = False
        self.inverted = False

    def setup(self):
        self.was_setup = True

    def cmd(self, command):
        self.commands.append(command)

    def tx(self, bytes):
        if self.inverted:
            for b in bytes:
                self.data.append(b ^ 0xFF)
        else:
            for b in bytes:
                self.data.append(b)

    def apply_inversion(self, b):
        if self.inverted:
            return b ^ 0xFF
        else:
            return b
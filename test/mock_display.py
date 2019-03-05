class MockDisplay:
    def __init__(self):
        self.was_setup = False
        self.was_shown = False
        self.drawings = []

    def setup(self):
        self.was_setup = True

    def draw_byxels(self, x, r, width, rows, byxels):
        self.drawings.append([x, r, width, rows, byxels])

    def draw_text(self, x, r, msg):
        self.drawings.append([x, r, msg])

    def show(self):
        self.was_shown = True
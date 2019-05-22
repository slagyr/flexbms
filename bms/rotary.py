class Rotary:
    def __init__(self, dt, clk):
        self.dt = dt
        self.clk = clk
        self.pos = 0
        self.prev_pos = 0
        self.clicked = False

    def setup(self):
        pass

    def handle_click(self):
        self.clicked = True

    def has_update(self):
        return self.clicked or self.pos != self.prev_pos

    def rest(self):
        self.prev_pos = self.pos
        self.clicked = False

    def get_rel_pos(self):
        return self.pos - self.prev_pos

    def __str__(self):
        return "Rotary - clicked: " + str(self.clicked) + " position: " + str(self.pos) + " previous: " + str(self.prev_pos)

    def handle_rotate(self):
        dt = self.dt.value()
        self.pos += 1 if dt else -1

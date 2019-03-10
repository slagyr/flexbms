class Rotary:
    def __init__(self, encoder):
        self.encoder = encoder
        self.prev_pos = 0
        self.clicked = False

    def setup(self):
        pass

    def click(self):
        self.clicked = True

    def has_update(self):
        return self.clicked or self.encoder.position != self.prev_pos

    def rest(self):
        self.prev_pos = self.encoder.position
        self.clicked = False

    def get_rel_pos(self):
        return self.encoder.position - self.prev_pos

    def __str__(self):
        return "Rotary - clicked: " + str(self.clicked) + " position: " + str(self.encoder.position) + " previous: " + str(self.prev_pos)
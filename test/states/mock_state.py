class MockState:
    def __init__(self):
        self.tick_count = 0
        self.entered = False
        self.exited = False

    def tick(self):
        self.tick_count += 1

    def enter(self):
        self.entered = True

    def exit(self):
        self.exited = True

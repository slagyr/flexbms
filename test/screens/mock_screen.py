
class MockScreen():
    def __init__(self):
        self.was_entered = False
        self.was_updated = False
        self.controller = "Controller"
        self.idle_timeout = 42

    def enter(self):
        self.was_entered = True

    def update(self):
        self.was_updated = True

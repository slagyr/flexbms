
class MockScreen():
    def __init__(self):
        self.was_entered = False
        self.was_updated = False
        self.controller = "Controller"
        self.idle_timeout = 42
        self.barf_on_update = False

    def enter(self):
        self.was_entered = True

    def update(self):
        if self.barf_on_update:
            raise RuntimeError("BARF!!!")
        self.was_updated = True

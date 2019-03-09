from bms.display import Display
from bms.util import load_binary


class MockDisplay(Display):
    def __init__(self):
        super().__init__("I2C")
        self.was_setup = False
        self.was_shown = False


    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def setup(self):
        self.was_setup = True

    def show(self):
        self.was_shown = True

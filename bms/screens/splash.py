from bms.util import load_binary_into


class SplashScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 3

    def enter(self):
        # byxels = bms.bin.load("splash")
        # self.controller.display.draw_byxels(0, 0, 128, 8, byxels)
        display = self.controller.display
        load_binary_into("splash", display.buffer)
        display.draw_text(44, 7, "FlexBMS v1.0")
        display.show()

    def update(self):
        pass
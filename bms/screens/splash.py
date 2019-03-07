import bms.bin


class SplashScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 3

    def enter(self):
        byxels = bms.bin.load("splash")
        self.controller.display.draw_byxels(0, 0, 128, 8, byxels)
        self.controller.display.show()

    def update(self):
        pass
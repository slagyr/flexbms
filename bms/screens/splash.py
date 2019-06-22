from bms import fonts, version

from bms.util import load_binary_into


class SplashScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 3000

    def enter(self):
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        load_binary_into("splash", display.buffer)
        display.draw_text(50, 7, "FlexBMS " + version.name())
        display.show()

    def user_input(self):
        pass

    def update(self):
        pass

    def menu_name(self):
        return "Splash"

    def menu_sel(self):
        self.controller.set_screen(self)
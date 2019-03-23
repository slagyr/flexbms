from bms import fonts


class ChargedScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = None

    def user_input(self):
        if self.controller.rotary.clicked:
            self.controller.set_screen(self.controller.main_menu)

    def menu_name(self):
        return "Charged"

    def menu_sel(self):
        self.controller.set_screen(self)

    def enter(self):
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        display.clear()

        display.draw_text(0, 3, "Battery Fully Charged")
        display.show()

    def update(self):
        pass
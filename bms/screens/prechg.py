from bms import fonts


class PrechargeScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = None

    def user_input(self):
        if self.controller.rotary.clicked:
            self.controller.set_screen(self.controller.main_menu)

    def menu_name(self):
        return "Precharge"

    def menu_sel(self):
        self.controller.set_screen(self)

    def enter(self):
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        display.clear()

        display.draw_text(30, 3, "Pre-Charging")
        display.draw_text(18, 5, "Battery V:")
        self.update()

    def update(self):
        display = self.controller.display
        batt_v = self.controller.bq.batt_voltage()
        display.draw_text(84, 5, "{0:.1f}".format(batt_v))
        display.show()

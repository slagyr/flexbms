from bms import fonts


class LowVScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = None
        self.pack_v = "???"

    def user_input(self):
        if self.controller.rotary.clicked:
            self.controller.set_screen(self.controller.main_menu)

    def menu_name(self):
        return "Low Voltage"

    def menu_sel(self):
        self.controller.set_screen(self)

    def enter(self):
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        display.clear()

        display.draw_text(12, 3, "Please Charge Me!")
        display.draw_text(30, 5, "Pack V:")
        self.update()

    def update(self):
        display = self.controller.display
        v = self.controller.cells.serial_voltage()
        v_str = "{0:2.1f}".format(v)
        if v_str != self.pack_v:
            self.pack_v = v_str
            display.draw_text(78, 5, v_str)
        display.show()

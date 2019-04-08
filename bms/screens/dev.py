from bms import fonts


class DevScreen:

    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = None

    def user_input(self):
        if self.controller.rotary.clicked:
            self.controller.set_screen(self.controller.main_menu)

    def menu_name(self):
        return "Developer Info"

    def menu_sel(self):
        self.controller.set_screen(self)

    def enter(self):
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        display.clear()

        display.draw_text(0, 0, "State:")
        display.draw_text(12, 1, "DSG:")
        display.draw_text(12, 2, "CHG:")
        display.draw_text(6, 3, "PCHG:")
        display.draw_text(18, 4, "CP:")
        display.draw_text(0, 5, "PACKV:")
        display.draw_text(0, 6, "BATTV:")
        display.draw_text(0, 7, "SER V:")
        display.draw_text(84, 0, "PACK I:")
        display.draw_text(84, 2, "TEMP 1:")
        display.draw_text(84, 4, "TEMP 2:")
        display.draw_text(84, 6, "TEMP 3:")

        self.update()

    def update(self):
        controller = self.controller
        bq = controller.bq
        driver = controller.driver
        display = controller.display
        display.draw_text(42, 0, controller.sm.state.__class__.__name__[:6])
        display.draw_text(42, 1, str(bq.discharge()))
        display.draw_text(42, 2, str(bq.charge()))
        display.draw_text(42, 3, str(driver.precharge()))
        display.draw_text(42, 4, str(driver.chargepump()))
        display.draw_text(42, 5, "{0:2.3f}".format(driver.pack_voltage()))
        display.draw_text(42, 6, "{0:2.3f}".format(bq.batt_voltage()))
        display.draw_text(42, 7, "{0:2.3f}".format(controller.cells.serial_voltage()))
        display.draw_text(90, 1, "{0:2.1f}".format(bq.amperage))

        display.show()

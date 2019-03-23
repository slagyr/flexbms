from bms import fonts, bq
from bms.screens.home import HomeScreen


class AlertScreen(HomeScreen):

    def __init__(self, controller):
        super().__init__(controller)

    def enter(self):
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        display.clear()
        self.draw_all(display)

    def user_input(self):
        if self.controller.rotary.clicked:
            self.controller.sm.clear()

    def update(self):
        pass

    def draw_all(self, display):
        display.draw_text(8 * 6, 0, "ALERT")

        row = 2
        for fault in self.controller.bq.faults:
            if fault == bq.OVRD_ALERT:
                display.draw_text(0, row, "Alert Pin Override")
            elif fault == bq.UV:
                display.draw_text(0, row, "Under Voltage")
            elif fault == bq.OV:
                display.draw_text(0, row, "Over Voltage")
            elif fault == bq.SCD:
                display.draw_text(0, row, "Short Circuit in DCH")
            elif fault == bq.OCD:
                display.draw_text(0, row, "Over Current in DCH")
            row += 1

        display.fill_rect(0, 56, 128, 8)
        display.inverted = True
        display.draw_text(18, 7, "Click to Resume")
        display.inverted = False

        display.show()



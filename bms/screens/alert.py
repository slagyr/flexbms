from bms import fonts, bq


class AlertScreen:

    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = None

    def enter(self):
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        display.clear()
        self.draw_all(display)

    def user_input(self):
        if self.controller.rotary.clicked:
            self.controller.alert_msg = None
            self.controller.sm.clear()

    def update(self):
        pass

    def draw_all(self, display):
        display.draw_text(8 * 6, 0, "ALERT")

        row = 2

        if self.controller.alert_msg:
            display.draw_text(0, row, self.controller.alert_msg)
            row += 1

        for fault in self.controller.bq.faults:
            if fault == bq.DEVICE_XREADY:
                display.draw_text(0, row, "Device Not Ready")
            elif fault == bq.OVRD_ALERT:
                display.draw_text(0, row, "Alert Pin Override")
            elif fault == bq.UV:
                display.draw_text(0, row, "Undervoltage")
            elif fault == bq.OV:
                display.draw_text(0, row, "Overvoltage")
            elif fault == bq.SCD:
                display.draw_text(0, row, "Dischg Short Circuit")
            elif fault == bq.OCD:
                display.draw_text(0, row, "Discharge Overcurrent")
            row += 1

        display.fill_rect(0, 56, 128, 8)
        display.inverted = True
        display.draw_text(18, 7, "Click to Resume")
        display.inverted = False

        display.show()



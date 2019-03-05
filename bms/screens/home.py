import bms.bin

class HomeScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 6000

    def enter(self):
        display = self.controller.display
        display.clear()
        # display.set_font(bms.bin.load("font5x7"))
        display.draw_text(0, 0, "FlexBMS v1.0")
        # display.draw_vline(0, 16, 47)
        display.draw_hline(0, 16, 105)
        display.draw_dashed_hline(0, 24, 105, 1, 5)
        display.draw_dashed_hline(0, 34, 105, 1, 5)
        display.draw_dashed_hline(0, 44, 105, 1, 5)
        display.draw_hline(0, 54, 105)

        for i in range(15):
            display.draw_text(i * 7, 7, str((i + 1) % 10))

        display.show()
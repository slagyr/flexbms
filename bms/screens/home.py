import bms.bin

GRAPH_X = 0
GRAPH_Y = 14
GRAPH_W = 105
GRAPH_H = 40

class HomeScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 6000

    def enter(self):
        display = self.controller.display
        display.clear()
        display.draw_text(0, 0, "FlexBMS v1.0")
        display.draw_hline(0, 14, 105)
        display.draw_dashed_hline(0, 24, 105, 1, 5)
        display.draw_dashed_hline(0, 34, 105, 1, 5)
        display.draw_dashed_hline(0, 44, 105, 1, 5)
        display.draw_hline(0, 54, 105)

        for i in range(15):
            display.draw_text(i * 7, 7, str((i + 1) % 10))

        display.show()
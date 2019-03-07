import bms.bin

GRAPH_X = 0
GRAPH_Y = 14
GRAPH_W = 105
GRAPH_H = 40

class HomeScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 6000

    def draw_graph(self, display):
        cell_count = self.controller.cells.count
        display.draw_hline(0, 14, 105)
        display.draw_hline(0, 54, 105)
        col_width = int(GRAPH_W / cell_count)
        for i in range(cell_count):
            display.draw_text(i * col_width, 7, str((i + 1) % 10))

    def draw_cell_levels(self, display):
        cells = self.controller.cells
        cell_count = cells.count
        col_width = int(GRAPH_W / cell_count)
        bar_width = int(col_width / 2)
        x_offset = int((col_width - bar_width) / 2)
        display.draw_dashed_hline(0, 24, GRAPH_W, 1, 5)
        display.draw_dashed_hline(0, 34, GRAPH_W, 1, 5)
        display.draw_dashed_hline(0, 44, GRAPH_W, 1, 5)
        for i in range(cell_count):
            soc = cells.soc(i)
            bar_heigth = int(GRAPH_H * soc)
            bar_heigth = max(1, min(bar_heigth, 39))
            x = GRAPH_X + (col_width * i) + x_offset
            y = GRAPH_Y + GRAPH_H - bar_heigth
            display.fill_rect(x, y, bar_width, bar_heigth)

    def enter(self):
        display = self.controller.display
        display.clear()
        display.draw_text(0, 0, "FlexBMS v1.0")
        self.draw_graph(display)

        display.show()

    def update(self):
        display = self.controller.display
        self.draw_cell_levels(display)
        display.show()
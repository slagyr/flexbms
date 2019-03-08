
GRAPH_X = 0
GRAPH_Y = 14
GRAPH_W = 105
GRAPH_H = 40

class HomeScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 6000
        self.col_width = 7
        self.col_text_offset = 0

    def draw_graph(self, display):
        cell_count = self.controller.cells.count
        self.col_width = int(GRAPH_W / cell_count)
        self.col_text_offset = int((self.col_width - display.font_width()) / 2)
        display.draw_hline(0, GRAPH_Y - 1, GRAPH_W)
        display.draw_hline(0, GRAPH_Y + GRAPH_H, GRAPH_W)
        for i in range(cell_count):
            x = i * self.col_width + self.col_text_offset
            display.draw_text(x, 7, str((i + 1) % 10))

    def draw_cell_levels(self, display):
        display.erase(GRAPH_X, GRAPH_Y, GRAPH_W, GRAPH_H)
        display.draw_dashed_hline(0, 24, GRAPH_W, 1, 5)
        display.draw_dashed_hline(0, 34, GRAPH_W, 1, 5)
        display.draw_dashed_hline(0, 44, GRAPH_W, 1, 5)

        bq = self.controller.bq
        cells = self.controller.cells
        cell_count = cells.count
        col_width = int(GRAPH_W / cell_count)
        bar_width = int(col_width / 2)
        x_offset = int((col_width - bar_width) / 2)
        for cell in cells:
            soc = cell.soc()
            bar_heigth = int(GRAPH_H * soc)
            bar_heigth = max(1, min(bar_heigth, 39))
            x = GRAPH_X + (col_width * cell.index) + x_offset
            y = GRAPH_Y + GRAPH_H - bar_heigth
            display.fill_rect(x, y, bar_width, bar_heigth)
            if bq.is_cell_balancing(cell.id):
                x = cell.index * self.col_width + self.col_text_offset
                display.draw_text(x, 5, "B")

    def enter(self):
        display = self.controller.display
        display.clear()
        display.draw_text(0, 0, "FlexBMS v1.0")
        display.draw_text(GRAPH_X + GRAPH_W - 1, 0, "BatV")
        display.draw_text(GRAPH_X + GRAPH_W - 1, 2, "SerV")
        self.draw_graph(display)

        display.show()

    def update(self):
        display = self.controller.display
        self.draw_cell_levels(display)
        x = GRAPH_X + GRAPH_W - 1
        display.draw_text(x, 1, "{:.1f}".format(self.controller.bq.batt_voltage()))
        display.draw_text(x, 3, "{:.1f}".format(self.controller.cells.serial_voltage()))
        display.show()
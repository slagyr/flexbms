from bms.util import clocked_fn

class HomeCell:
    def __init__(self):
        self.h = 0
        self.bal = False
        self.changed = False

    def update(self, h, bal):
        self.changed = (h != self.h) or (bal != self.bal)
        self.h = h
        self.bal = bal


class HomeScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 6000
        self.col_width = 7
        self.col_text_offset = 0
        self.display_cells = []

    def draw_graph_labels(self, display):
        cell_count = self.controller.cells.count
        self.col_width = int(105 / cell_count)
        self.col_text_offset = int((self.col_width - display.font_width()) / 2)
        self.draw_graph_guidelines(display)
        for i in range(cell_count):
            x = i * self.col_width + self.col_text_offset
            display.draw_text(x, 7, str((i + 1) % 10))

    def draw_cell_levels(self, display):
        bq = self.controller.bq
        cells = self.controller.cells
        col_width = self.col_width
        bar_width = int(col_width / 2)
        x_offset = int((col_width - bar_width) / 2)
        for cell in cells:
            self.draw_graph_bar(bar_width, bq, cell, col_width, display, x_offset)

    def draw_graph_bar(self, bar_width, bq, cell, col_width, display, x_offset):
        soc = cell.soc()
        bar_height = max(1, min(int(40 * soc), 39))
        display_cell = self.display_cells[cell.index]
        display_cell.update(bar_height, cell.balancing)
        if display_cell.changed:
            x = 0 + (col_width * cell.index) + x_offset
            y = 14 + 40 - bar_height
            display.erase(x, 14, bar_width, 40)
            if bq.is_cell_balancing(cell.id):
                display.draw_rect(x, y, bar_width, bar_height)
            else:
                display.fill_rect(x, y, bar_width, bar_height)

    def draw_graph_guidelines(self, display):
        spacing = self.col_width - 1
        display.draw_dashed_hline(0, 24, 105, 1, spacing)
        display.draw_dashed_hline(0, 34, 105, 1, spacing)
        display.draw_dashed_hline(0, 44, 105, 1, spacing)
        display.draw_hline(0, 14 - 1, 105)
        display.draw_hline(0, 14 + 40, 105)

    def enter(self):
        for _ in self.controller.cells:
            self.display_cells.append(HomeCell())

        display = self.controller.display
        display.clear()
        display.draw_text(0, 0, "Flex BMS v1.0")
        display.draw_text(0 + 104, 0, "BatV")
        display.draw_text(0 + 104, 2, "SerV")
        display.draw_text(0 + 104, 4, "PakV")
        self.draw_graph_labels(display)

        display.show()

    def update(self):
        display = self.controller.display
        self.draw_cell_levels(display)
        display.draw_text(104, 1, "{:.1f}".format(self.controller.bq.batt_voltage()))
        display.draw_text(104, 3, "{:.1f}".format(self.controller.cells.serial_voltage()))
        display.show()

from bms import fonts


class DisplayCell:
    def __init__(self):
        self.v = 0
        self.bal = False
        self.changed = False

    def update(self, v, bal):
        self.changed = (v != self.v) or (bal != self.bal)
        self.v = v
        self.bal = bal


class BargraphScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = None
        self.col_width = 7
        self.col_text_offset = 0
        self.display_cells = None

    def menu_name(self):
        return "Cell Bar Graph"

    def menu_sel(self):
        self.controller.set_screen(self)

    def user_input(self):
        if self.controller.rotary.clicked:
            self.controller.set_screen(self.controller.main_menu)

    def enter(self):
        self.reset_display_cells()
        self.draw_full()

    # borrows by VoltagesScreen
    def reset_display_cells(self):
        if self.display_cells is None:
            self.display_cells = []
            for _ in self.controller.cells:
                self.display_cells.append(DisplayCell())
        else:
            for cell in self.display_cells:
                cell.v = 0
        return self.display_cells

    def update(self):
        display = self.controller.display
        self.draw_cell_levels(display)
        chg = "<" if self.controller.bq.charge() else "|"
        dsg = ">" if self.controller.bq.discharge() else "|"
        pchg = "P" if self.controller.driver.precharge() else "-"
        statstr = chg + pchg + dsg
        display.draw_text(0, 0, statstr)
        display.draw_text(60, 0, "{:.1f}".format(self.controller.bq.amperage * -1))
        display.draw_text(104, 1, "{:.1f}".format(self.controller.bq.batt_voltage()))
        display.draw_text(104, 3, "{:.1f}".format(self.controller.cells.serial_voltage()))
        display.draw_text(104, 5, "{:.1f}".format(self.controller.driver.pack_voltage()))
        display.show()

    def draw_full(self):
        display = self.controller.display
        display.inverted = False
        display.font = fonts.font6x8()
        display.clear()
        display.draw_text(24, 0, "Amps:")
        display.draw_text(104, 0, "BatV")
        display.draw_text(104, 2, "SerV")
        display.draw_text(104, 4, "PakV")
        self.draw_graph_labels(display)
        self.update()

    def draw_graph_labels(self, display):
        cell_count = len(self.display_cells)
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
            if display_cell.bal:
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

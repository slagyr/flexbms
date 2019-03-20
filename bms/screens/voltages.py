from bms import fonts


class VoltagesScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = 6000000
        self.display_cells = None

    def menu_name(self):
        return "Cell Voltages"

    def menu_sel(self):
        self.controller.set_screen(self)

    def enter(self):
        self.display_cells = self.controller.home_screen.reset_display_cells()
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        display.clear()
        for i in range(len(self.display_cells)):
            label = "{0:2d}) ".format(i + 1)
            x = 0
            row = i
            if row > 7:
                x = 60
                row = i - 8
            display.draw_text(x, row, label)
        self.draw_update()

    def update(self):
        if self.controller.rotary.clicked:
            self.controller.set_screen(self.controller.main_menu)
        else:
            self.draw_update()

    def draw_update(self):
        display = self.controller.display
        for cell in self.controller.cells:
            str_val = "{0:1.3f}".format(cell.voltage)
            display_cell = self.display_cells[cell.index]
            display_cell.update(str_val, cell.balancing)
            if display_cell.changed:
                i = cell.index
                x = 24
                row = i
                if row > 7:
                    x = 84
                    row = i - 8
                display.inverted = True if cell.balancing else False
                display.erase(x, row * 8, 30, 8)
                display.draw_text(x, row, str_val)
                display.inverted = False if cell.balancing else True
        display.show()

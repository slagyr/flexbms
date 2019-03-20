from bms import fonts


class Menu:
    def __init__(self, controller, title):
        self.controller = controller
        self.title = title
        self.items = []
        self.highlighted = 0
        self.idle_timeout = 5000

    def enter(self):
        self.highlighted = 0
        display = self.controller.display
        display.font = fonts.font6x8()
        display.inverted = False
        display.clear()
        self.draw_all(display)

    def update(self):
        rotary = self.controller.rotary
        my = self
        if not rotary.has_update():
            return
        if rotary.clicked:
            item = my.items[my.highlighted]
            item.menu_sel()
        elif rotary.get_rel_pos() != 0:
            highlighted = my.highlighted + rotary.get_rel_pos()
            if highlighted < 0:
                highlighted = 0
            elif highlighted > len(my.items) - 1:
                highlighted = len(my.items) - 1
            if my.highlighted != highlighted:
                previous = my.highlighted
                my.highlighted = highlighted
                my.draw_update(previous)

    def add(self, item):
        self.items.append(item)

    def draw_all(self, display):
        title = "" + self.title + " MENU".upper()[:21]
        offset = int((21 - len(title)) / 2)
        display.draw_text(offset * 6, 0, title)
        for i in range(len(self.items)):
            if i == self.highlighted:
                self.draw_highlted_item(display, i)
            else:
                self.draw_item(display, i)
        display.show()

    def draw_update(self, previous):
        display = self.controller.display
        display.erase(0, (previous + 1) * 8, 128, 8)
        self.draw_item(display, previous)
        self.draw_highlted_item(display, self.highlighted)
        display.show()

    def draw_highlted_item(self, display, i):
        item = self.items[i]
        text = str(i + 1) + ") " + item.menu_name()[:21]
        display.fill_rect(0, (i + 1) * 8, 128, 8)
        display.inverted = True
        display.draw_text(0, i + 1, text)
        display.inverted = False

    def draw_item(self, display, i):
        item = self.items[i]
        text = str(i + 1) + ") " + item.menu_name()[:21]
        display.draw_text(0, i + 1, text)

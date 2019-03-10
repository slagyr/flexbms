class Events:
    def __init__(self, buttons):
        self.buttons = buttons
        self.dispatchers = []

    def dispatch(self):
        pressed = self.buttons.get_pressed()
        for i in range(len(self.dispatchers)):
            if pressed & (1 << i):
                dispatcher = self.dispatchers[i]
                dispatcher()


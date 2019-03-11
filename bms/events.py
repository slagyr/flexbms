class Events:
    def __init__(self, buttons):
        self.last_sample = 0
        self.buttons = buttons
        self.listeners = []

    def dispatch(self):
        sample = self.buttons.get_pressed()
        for i in range(len(self.listeners)):
            now = sample & (1 << i)
            before = self.last_sample & (1 << i)
            if now and not before:
                self.listeners[i].pressed()
            if before and not now:
                self.listeners[i].released()
        self.last_sample = sample

    def setup(self):
        pass


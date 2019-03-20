class MockPin:
    def __init__(self):
        self.val = False

    def value(self, v=None):
        if v:
            self.val = v
        else:
            return self.val

class MockADC:
    def __init__(self):
        self.value = 0

    def read(self):
        return self.value

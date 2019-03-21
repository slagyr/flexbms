class MockPin:
    def __init__(self):
        self.val = False

    def value(self, v=None):
        if v is None:
            return self.val
        else:
            self.val = v

class MockADC:
    def __init__(self):
        self.value = 0

    def read(self):
        return self.value

class MockClock:
    def __init__(self):
        self.mils = 0

    def millis(self):
        return self.mils

    def millis_since(self, then):
        return self.mils - then

    def millis_after(self, time, millis):
        return time + millis

    def sleep(self, millis):
        pass

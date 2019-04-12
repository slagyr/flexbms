class MockClock:
    def __init__(self, mils=0):
        self.mils = mils

    def millis(self):
        return self.mils

    def millis_since(self, then):
        return self.mils - then

    def millis_diff(self, after, before):
        return after - before

    def millis_add(self, time, millis):
        return time + millis

    def sleep(self, millis):
        pass

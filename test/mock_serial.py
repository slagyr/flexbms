from bms.serial import Serial


class MockSerial(Serial):
    def __init__(self):
        self.was_setup = False
        self.was_closed = False
        self.setup() # so that tests don't have to

    def setup(self):
        self.out = []
        self.was_setup = True

    def close(self):
        self.was_closed = True

    def _append(self, l):
        self.out.append(l)

    def count_log_type(self, type):
        count = 0
        for line in self.out:
            if line.startswith(type):
                count += 1
        return count


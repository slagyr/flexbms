from bms.logger import Logger


class MockLogger(Logger):
    def __init__(self):
        self.was_setup = False
        self.was_closed = False
        self.setup() # so that tests don't have to

    def setup(self):
        self.log = []
        self.was_setup = True

    def close(self):
        self.was_closed = True

    def _append(self, l):
        self.log.append(l)

    def count_log_type(self, type):
        count = 0
        for line in self.log:
            if line.startswith(type):
                count += 1
        return count


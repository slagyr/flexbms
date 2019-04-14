from bms.logger import Logger


class MockLogger(Logger):
    def __init__(self):
        self.was_setup = False
        self.was_closed = False
        self.setup() # so that tests don't have to

    def setup(self):
        self.cell_log = []
        self.temp_log = []
        self.msg_log = []
        self.pack_log = []
        self.was_setup = True

    def close(self):
        self.was_closed = True

    def _append_line(self, f, l):
        f.append(l)


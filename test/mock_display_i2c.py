class MockDisplayI2C:
    def __init__(self):
        self.locked = False
        self.lock_count = 0
        self.writes = []
        self.scan_result = []

    def send(self, bytes, address, **kwargs):
        self.writes.append([address, bytes])

    def scan(self):
        return self.scan_result

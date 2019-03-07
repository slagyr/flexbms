class MockDisplayI2C:
    def __init__(self):
        self.locked = False
        self.lock_count = 0
        self.writes = []
        self.scan_result = []

    def writeto(self, address, bytes, **kwargs):
        self.writes.append([address, bytes])

    def try_lock(self):
        if self.locked:
            return False
        else:
            self.locked = True
            self.lock_count += 1
            return True

    def unlock(self):
        self.locked = False

    def scan(self):
        return self.scan_result

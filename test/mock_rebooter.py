class MockRebooter():
    def __init__(self):
        self.was_rebooted = False

    def reboot(self):
        self.was_rebooted = True
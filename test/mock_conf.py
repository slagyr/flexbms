from bms.conf import Config


class MockConfig(Config):
    def __init__(self):
        super().__init__()
        self.was_saved = False

    def save(self):
        super().save()
        self.was_saved = True



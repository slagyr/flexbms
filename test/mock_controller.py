from mock_display import MockDisplay


class MockController:
    def __init__(self):
        self.display = MockDisplay()
        self.screen = None


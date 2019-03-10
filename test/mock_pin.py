class MockPin:
    def __init__(self):
        self.value = False

    def switch_to_input(self):
        self.mode = "input"

    def switch_to_output(self):
        self.mode = "output"
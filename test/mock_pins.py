class MockDPin:
    def __init__(self):
        self.val = False
        # self.direction = "unset"

    def value(self, v=None):
        if v:
            self.val = v
        else:
            return self.val

    # def switch_to_output(self):
    #     self.direction = "output"
    #
    # def switch_to_input(self):
    #     self.direction = "input"

class MockAPin:
    def __init__(self):
        self.value = 0
        self.reference_voltage = 3.3

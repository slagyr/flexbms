class MockVCP:

    def __init__(self):
        self.input = []
        self.output = []

    def readline(self):
        line = self.input[0]
        if line is not None:
            self.input = self.input[1:]
        return line.encode("utf-8")

    def write(self, line):
        self.output.append(line)
from bms.temps import Temps


class MockTemps(Temps):

    def __init__(self, bq):
        super().__init__(bq)
        self.stub_temp1 = 21
        self.stub_temp2 = 22
        self.stub_temp3 = 23

    def load(self):
        super().load()
        self.temp1 = self.stub_temp1
        self.temp2 = self.stub_temp2
        self.temp3 = self.stub_temp3



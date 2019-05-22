from bms.pack import Pack


class MockPack(Pack):
    def __init__(self, bq, driver):
        super().__init__(bq, driver)
        self.stub_amps_in = None
        self.stub_batt_v = None
        self.stub_pack_v = None

    def load(self):
        super().load()
        if self.stub_amps_in is not None:
            self.amps_in = self.stub_amps_in
        if self.stub_batt_v is not None:
            self.batt_v = self.stub_batt_v
        if self.stub_pack_v is not None:
            self.pack_v = self.stub_pack_v
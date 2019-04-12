class Pack:
    def __init__(self, bq, driver):
        self.bq = bq
        self.driver = driver
        self.batt_v = 0.0
        self.pack_v = 0.0
        self.amps = 0.0
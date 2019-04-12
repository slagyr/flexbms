class Pack:
    def __init__(self, bq, driver):
        self.bq = bq
        self.driver = driver
        self.batt_v = 0.0
        self.pack_v = 0.0
        self.amps = 0.0
        self.loaded = False

    def load(self):
        my = self
        if my.loaded:
            return
        my.batt_v = my.bq.batt_voltage()
        my.pack_v = my.driver.pack_voltage()
        my.amps = my.bq.amperage
        my.loaded = True

    def expire(self):
        self.loaded = False
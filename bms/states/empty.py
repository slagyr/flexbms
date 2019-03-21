class EmptyState():
    def __init__(self, sm):
        self.sm = sm

    def enter(self):
        bq = self.sm.controller.bq
        driver = self.sm.controller.driver
        bq.discharge(False)
        bq.charge(False)
        bq.adc(False)
        bq.cc(False)
        driver.chargepump(False)
        driver.packmonitor(False)
        driver.precharge(False)

    def tick(self):
        pass

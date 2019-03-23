class FullState:
    def __init__(self, sm):
        self.sm = sm

    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        driver = controller.driver

        bq.discharge(False)
        bq.charge(False)
        bq.adc(True)
        driver.chargepump(True)
        driver.precharge(False)
        controller.sm_tick_interval(500)
        controller.set_home_screen(controller.charged_screen)

    def tick(self):
        my = self
        cells = my.sm.controller.cells
        driver = my.sm.controller.driver
        bq = my.sm.controller.bq

        if not cells.fully_charged():
            my.sm.norm_v()
        elif driver.pack_voltage() < bq.batt_voltage():
            my.sm.pow_off()
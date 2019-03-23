class PreChgState:

    def __init__(self, sm):
        self.sm = sm

    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        driver = controller.driver

        bq.discharge(True)
        bq.charge(False)
        bq.adc(True)
        driver.chargepump(True)
        driver.precharge(True)
        controller.sm_tick_interval(500)
        controller.set_home_screen(controller.prechg_screen)

    def tick(self):
        my = self
        controller = my.sm.controller
        bq = controller.bq
        cells = controller.cells
        driver = controller.driver

        if driver.pack_voltage() < bq.batt_voltage():
            my.sm.pow_off()
        elif not cells.has_low_voltage():
            my.sm.norm_v()

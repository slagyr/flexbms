class ErrorState:
    def __init__(self, sm):
        self.sm = sm

    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        driver = controller.driver

        bq.discharge(False)
        bq.charge(False)
        bq.adc(False)
        driver.chargepump(False)
        driver.precharge(False)
        controller.sm_tick_interval(3600000)
        controller.set_home_screen(controller.error_screen)
        controller.set_screen(controller.error_screen)

    def tick(self):
        controller = self.sm.controller
        controller.loaded_pack()
        controller.loaded_cells()
        controller.loaded_temps()

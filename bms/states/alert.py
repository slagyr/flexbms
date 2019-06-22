class AlertState():
    def __init__(self, sm):
        self.sm = sm

    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        driver = controller.driver

        try:
            controller.log("Alert: " + str(controller.alert_msg) + ":" + str(bq.faults))
        except OSError:
            pass

        bq.discharge(False)
        bq.charge(False)
        bq.adc(False)
        driver.chargepump(False)
        driver.precharge(False)
        controller.sm_tick_interval(10000)
        controller.set_home_screen(controller.alert_screen)
        controller.set_screen(controller.alert_screen)

    def tick(self):
        pass

    def exit(self):
        self.sm.controller.alert_msg = None
        self.sm.controller.bq.clear_sys_stat()


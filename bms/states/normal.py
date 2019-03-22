from bms import util


class NormalState:
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
        driver.precharge(False)
        controller.sm_tick_interval(500)
        controller.set_home_screen(controller.bargraph_screen)

    def tick(self):
        controller = self.sm.controller
        controller.bq.cc_oneshot()
        controller.bq.load_cell_voltages(controller.cells)
        controller.screen_outdated(True)

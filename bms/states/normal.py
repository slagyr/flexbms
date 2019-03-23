from bms import util



class NormalState:
    def __init__(self, sm):
        self.sm = sm
        self.chg_fet_on = False
        self.counter = 0

    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        driver = controller.driver

        bq.discharge(True)
        bq.charge(False)
        bq.adc(False)
        bq.cc_oneshot()
        driver.chargepump(True)
        driver.precharge(False)
        controller.sm_tick_interval(500)
        controller.set_home_screen(controller.bargraph_screen)

        self.chg_fet_on = False
        self.counter = 0

    def tick(self):
        my = self
        controller = my.sm.controller
        bq = controller.bq
        cells = controller.cells

        bq.cc_oneshot()

        if not my.chg_fet_on and bq.amperage < -0.1: # outbound current detected
            bq.charge(True)
            my.chg_fet_on = True
        elif my.chg_fet_on and bq.amperage > -0.1: # current goes away
            bq.charge(False)
            my.chg_fet_on = False

        pack_V = controller.driver.pack_voltage()
        batt_V = bq.batt_voltage()
        if pack_V > batt_V:
            my.sm.pow_on()
        elif my.counter == 8:
            bq.adc(True)
        elif my.counter == 9:
            bq.load_cell_voltages(cells)
            bq.adc(False)
            my.counter = -1
            if cells.has_low_voltage():
                my.sm.low_v()
        my.counter += 1

        controller.screen_outdated(True)

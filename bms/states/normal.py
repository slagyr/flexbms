from bms.conf import CONF


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
        bq.charge(True)
        bq.adc(False)
        bq.cc_oneshot()
        driver.chargepump(True)
        driver.precharge(False)
        controller.sm_tick_interval(500)

        self.chg_fet_on = False
        self.counter = 0

    def tick(self):
        my = self
        controller = my.sm.controller
        bq = controller.bq

        bq.cc_oneshot()
        pack = controller.loaded_pack()

        # if not my.chg_fet_on and pack.amps_in < -0.1: # outbound current detected
        #     bq.charge(True)
        #     my.chg_fet_on = True
        # elif my.chg_fet_on and pack.amps_in > -0.1: # current goes away
        #     bq.charge(False)
        #     my.chg_fet_on = False

        if pack.amps_in > (CONF.CELL_PARALLEL * CONF.CELL_MAX_DSG_I + CONF.PACK_I_TOLERANCE):
            controller.trigger_alert("Discharge Overcurrent")
        elif (pack.pack_v - CONF.PACK_V_TOLERANCE) > pack.batt_v:
            my.sm.pow_on()
        elif my.counter == 8:
            bq.adc(True)
        elif my.counter == 9:
            cells = controller.loaded_cells()
            temps = controller.loaded_temps()
            bq.adc(False)
            my.counter = -1
            if cells.has_low_voltage():
                my.sm.low_v()
            elif temps.temp1 > CONF.TEMP_MAX_PACK_DSG:
                controller.trigger_alert("Discharge Over-Temp")
            elif temps.temp1 < CONF.TEMP_MIN_PACK_DSG:
                controller.trigger_alert("Discharge Under-Temp")
        my.counter += 1

        controller.screen_outdated(True)

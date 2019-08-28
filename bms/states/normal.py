from bms.conf import CONF


class NormalState:
    def __init__(self, sm):
        self.sm = sm
        self.chg_fet_on = False
        self.counter = 0
        self.ocd_grace_counter = 0
        self.power_on_counter = 0
        self.max_current = 0

    def enter(self):
        self.max_current = CONF.CELL_PARALLEL * CONF.CELL_MAX_DSG_I + CONF.PACK_I_TOLERANCE
        # TODO - Would like to put in constructor but CONF hasn't been loaded
        
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
        self.ocd_grace_counter = 0
        self.power_on_counter = 0

    def tick(self):
        my = self
        controller = my.sm.controller
        bq = controller.bq

        bq.cc_oneshot()
        pack = controller.loaded_pack()

        if not my.chg_fet_on and pack.amps_in < -0.1: # outbound current detected
            bq.charge(True)
            my.chg_fet_on = True
        elif my.chg_fet_on and pack.amps_in > -0.1: # current goes away
            bq.charge(False)
            my.chg_fet_on = False

        if self.is_discharge_overcurrent(pack):
            controller.trigger_alert("Discharge Overcurrent (M)")
        elif self.is_power_detected(pack):
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

    def is_discharge_overcurrent(self, pack):
        amps_out = pack.amps_in * -1
        self.sm.controller.log("self.max_current: " + str(self.max_current))
        self.sm.controller.log("amps_out: " + str(amps_out))
        if amps_out > self.max_current + CONF.PACK_OCD_TOLERANCE:
            return True
        elif amps_out > self.max_current:
            if self.ocd_grace_counter > 0:
                return True
            else:
                self.ocd_grace_counter += 1
                return False
        else:
            self.ocd_grace_counter = 0
            return False

    def is_power_detected(self, pack):
        if pack.batt_v < (pack.pack_v - CONF.PACK_V_TOLERANCE) and pack.amps_in > -1.0:
            if self.power_on_counter > 0:
                return True
            else:
                self.power_on_counter += 1
                return False
        else:
            self.power_on_counter = 0
            return False

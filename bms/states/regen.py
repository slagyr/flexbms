from bms.conf import CONF

class RegenState():
    def __init__(self, sm):
        self.sm = sm
        self.balance_counter = 0

    def check_charger_voltage(self, pack):
        controller = self.sm.controller
        voltage = pack.pack_v
        # TODO - Greceful handling of this... add delay before trigger
        if voltage > controller.cells.max_serial_voltage() + CONF.PACK_V_TOLERANCE:
            controller.alert_msg = "Wrong Charge V: {0:.1f}".format(voltage)
            self.sm.alert()
            return False
        return True


    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        driver = controller.driver

        self.balance_counter = 0

        pack = controller.loaded_pack()
        if not self.check_charger_voltage(pack):
            return

        bq.discharge(True)
        bq.charge(True)
        bq.adc(True)
        driver.chargepump(True)
        driver.precharge(False)
        controller.sm_tick_interval(500)


    def exit(self):
        self.sm.controller.cells.reset_balancing()

    def tick(self):
        my = self
        controller = my.sm.controller
        bq = controller.bq
        conf = CONF

        bq.cc_oneshot()
        cells = controller.loaded_cells()
        pack = controller.loaded_pack()
        temps = controller.loaded_temps()

        if pack.amps_in > (conf.CELL_MAX_CHG_I * conf.CELL_PARALLEL + CONF.PACK_I_TOLERANCE):
            controller.trigger_alert("Charge Overcurrent")
        elif temps.temp1 > CONF.TEMP_MAX_PACK_CHG:
            controller.trigger_alert("Charge Over-Temp")
        elif temps.temp1 < CONF.TEMP_MIN_PACK_CHG:
            controller.trigger_alert("Charge Under-Temp")
        # elif cells.has_low_voltage():
        #     my.sm.low_v()
        elif cells.any_cell_full():
            bq.charge(False)
        elif pack.batt_v > pack.pack_v + CONF.PACK_V_TOLERANCE:
            my.sm.pow_off()
        # elif not self.check_charger_voltage(pack):
        #     pass # alert event already triggered in check_charger_voltage()




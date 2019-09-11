

class ChargeState:
    def __init__(self, sm):
        self.sm = sm
        self.balance_counter = 0

    def check_charger_voltage(self, pack):
        controller = self.sm.controller
        voltage = pack.pack_v
        # TODO - Greceful handling of this... add delay before trigger
        if voltage > controller.cells.max_serial_voltage() + controller.conf.PACK_V_TOLERANCE:
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

        bq.discharge(False)
        bq.charge(True)
        bq.adc(True)
        driver.chargepump(True)
        driver.precharge(False)
        controller.sm_tick_interval(1000)

    def exit(self):
        cells = self.sm.controller.cells
        self.stop_balancing(cells, self.sm.controller)

    def tick(self):
        my = self
        controller = my.sm.controller
        bq = controller.bq
        conf = controller.conf

        bq.cc_oneshot()
        cells = controller.loaded_cells()
        pack = controller.loaded_pack()
        temps = controller.loaded_temps()

        if pack.amps_in > (conf.CELL_MAX_CHG_I * conf.CELL_PARALLEL + conf.PACK_I_TOLERANCE):
            controller.trigger_alert("Charge Overcurrent")
        elif temps.temp1 > conf.TEMP_MAX_PACK_CHG:
            controller.trigger_alert("Charge Over-Temp")
        elif temps.temp1 < conf.TEMP_MIN_PACK_CHG:
            controller.trigger_alert("Charge Under-Temp")
        elif not self.check_charger_voltage(pack):
            pass # alert event already triggered
        elif cells.has_low_voltage():
            my.sm.low_v()
        elif self.balance_counter == 0 and cells.fully_charged(conf.CELL_V_TOLERANCE):
            my.sm.full_v()
        else:
            has_charge_current = pack.amps_in > (0 + conf.PACK_I_TOLERANCE)
            bq.discharge(has_charge_current)
            if self.balance_counter == 0:
                if not has_charge_current and pack.pack_v < pack.batt_v - 2:
                    my.sm.pow_off()
                else:
                    self.start_balancing(bq, cells, controller)
            elif self.balance_counter == 60:
                self.stop_balancing(cells, controller)
            elif self.balance_counter == 66:
                bq.discharge(False) # So we can measure raw PackV next tick
                self.balance_counter = -1

            self.balance_counter += 1

    def stop_balancing(self, cells, controller):
        cells.reset_balancing()
        controller.serial.balance(cells)

    def start_balancing(self, bq, cells, controller):
        cells.update_balancing()
        controller.serial.balance(cells)
        if cells.any_cell_full(controller.conf.CELL_V_TOLERANCE):
            bq.charge(False)
            bq.discharge(False)
        else:
            bq.charge(True)





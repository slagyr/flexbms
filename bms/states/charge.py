class ChargeState():
    def __init__(self, sm):
        self.sm = sm
        self.balance_counter = 0

    def check_charger_voltage(self):
        controller = self.sm.controller
        voltage = controller.driver.pack_voltage()
        if voltage > controller.cells.max_serial_voltage() + 0.5:
            controller.alert_msg = "Wrong Charge V: {0:.1f}".format(voltage)
            self.sm.alert()
            return False
        return True

    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        driver = controller.driver

        self.balance_counter = 0

        if(self.check_charger_voltage()):
            bq.discharge(True)
            bq.charge(True)
            bq.adc(True)
            driver.chargepump(True)
            driver.precharge(False)
            controller.sm_tick_interval(500)
            controller.set_home_screen(controller.voltages_screen)


    def exit(self):
        self.sm.controller.cells.reset_balancing(self.sm.controller.bq)

    def tick(self):
        my = self
        controller = my.sm.controller
        bq = controller.bq
        cells = controller.cells
        driver = controller.driver

        bq.cc_oneshot()
        bq.load_cell_voltages(cells)

        if bq.amperage > 1.5:
            controller.alert_msg = "Charge Overcurrent"
            my.sm.alert()
        elif cells.has_low_voltage():
            my.sm.low_v()
        elif driver.pack_voltage() < bq.batt_voltage():
            my.sm.pow_off()
        elif not self.check_charger_voltage():
            pass # alert event already triggered
        elif self.balance_counter == 0:
            if cells.fully_charged():
                my.sm.full_v()
            else:
                cells.update_balancing(bq)
            bq.charge(not cells.any_cell_full())
        elif self.balance_counter == 60:
            cells.reset_balancing(bq)
        elif self.balance_counter == 66:
            self.balance_counter = -1
        self.balance_counter += 1

        controller.screen_outdated(True)




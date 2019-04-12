from bms.conf import CONF


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

        pack = controller.loaded_pack()
        cells = controller.loaded_cells()
        temps = controller.loaded_temps()

        if (pack.pack_v + CONF.PACK_V_TOLERANCE) < pack.batt_v:
            my.sm.pow_off()
        elif not cells.has_low_voltage():
            my.sm.norm_v()

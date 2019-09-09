

class FullState:
    def __init__(self, sm):
        self.sm = sm

    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        driver = controller.driver

        bq.discharge(False)
        bq.charge(False)
        bq.adc(True)
        driver.chargepump(True)
        driver.precharge(False)
        controller.sm_tick_interval(500)

    def tick(self):
        my = self
        sm = my.sm
        controller = sm.controller
        bq = controller.bq

        bq.discharge(False)
        bq.charge(False)

        pack = controller.loaded_pack()
        cells = controller.loaded_cells()
        controller.loaded_temps()

        if not cells.fully_charged(-1 * controller.conf.CELL_V_TOLERANCE):
            sm.norm_v()
        elif pack.pack_v < pack.batt_v - 2:
            sm.pow_off()
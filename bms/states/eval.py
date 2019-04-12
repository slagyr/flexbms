from bms.conf import CONF


class EvalState():
    def __init__(self, sm):
        self.sm = sm

    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        bq.discharge(False)
        bq.charge(False)
        controller.sm_tick_interval(500)

    def tick(self):
        controller = self.sm.controller
        driver = controller.driver

        controller.loaded_pack()
        cells = controller.loaded_cells()
        controller.loaded_temps()

        if cells.has_low_voltage():
            self.sm.low_v()
        elif driver.pack_voltage() > (cells.serial_voltage() + CONF.PACK_V_TOLERANCE):
            self.sm.pow_on()
        else:
            self.sm.norm_v()

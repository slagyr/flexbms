
from bms.util import log


class StandbyState():
    def __init__(self, sm):
        self.sm = sm
        self.in_wake_cycle = False

    def enter(self):
        controller = self.sm.controller
        bq = controller.bq
        driver = controller.driver

        bq.discharge(False)
        bq.charge(False)
        bq.adc(False)
        bq.cc(False)
        driver.chargepump(False)
        driver.packmonitor(False)
        driver.precharge(False)

        controller.sm_tick_interval(400)
        self.tick_count = 0

    def tick(self):
        controller = self.sm.controller

        if self.in_wake_cycle:
            self.in_wake_cycle = False

            pack = controller.loaded_pack()
            cells = controller.loaded_cells()
            controller.loaded_temps()

            if cells.has_low_voltage():
                self.sm.low_v()
            elif (pack.pack_v - controller.conf.PACK_V_TOLERANCE) > pack.batt_v:
                self.sm.pow_on()
            else:
                controller.bq.adc(False)
                controller.sm_tick_interval(400)
                controller.screen_outdated(True)
        else:
            self.in_wake_cycle = True
            controller.bq.adc(True) # get ADC warmed up
            controller.sm_tick_interval(100)


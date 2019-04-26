from bms.conf import CONF
from bms.util import log


class EmptyState():
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

        controller.sm_tick_interval(100)
        controller.set_home_screen(controller.low_v_screen)

    def tick(self):
        controller = self.sm.controller

        if self.in_wake_cycle:
            self.in_wake_cycle = False

            pack = controller.loaded_pack()
            controller.loaded_cells()
            controller.loaded_temps()

            if (pack.pack_v - CONF.PACK_V_TOLERANCE) > pack.batt_v:
                self.sm.pow_on()
            else:
                controller.bq.adc(False)
                controller.sm_tick_interval(10000)
                controller.screen_outdated(True)
        else:
            self.in_wake_cycle = True
            controller.bq.adc(True) # get ADC warmed up
            controller.sm_tick_interval(500)


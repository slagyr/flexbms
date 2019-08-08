from bms import util
from bms.conf import CONF, CONF_FILE
from bms.util import log


class Hardware():

    def __init__(self, controller):
        self.controller = controller

    def calibrate_pack_v(self):
        log("Calibrating Pack Voltage")
        driver = self.controller.driver
        bq = self.controller.bq
        cells = self.controller.cells

        cells.expire()
        cells.load()
        serial_v = cells.serial_voltage()
        batt_v = bq.batt_voltage()
        pack_v = (serial_v + batt_v) / 2
        log("pack_v: " + str(pack_v))

        driver.chargepump(True)
        bq.discharge(False)
        bq.charge(False)
        util.clock.sleep(1000)
        offset = driver.sample_adc()
        log("offset: " + str(offset))

        bq.discharge(True)
        bq.charge(True)
        util.clock.sleep(1000)
        loaded_adc = driver.sample_adc()
        gain = pack_v / (loaded_adc - offset)
        log("gain: " + str(gain))

        driver.chargepump(False)
        bq.discharge(False)
        bq.charge(False)

        CONF.PACK_V_OFFSET = offset
        CONF.PACK_V_GAIN = gain
        CONF.save()
        log(CONF_FILE + " updated")

    def test_balancers(self):
        log("Testing Balancing Circuits")
        log("Use thermal camera to watch balancing resistors heat up one after the other.")
        loops = 3
        log("Looping " + str(loops) + " times")
        cells = self.controller.cells
        bq = self.controller.bq
        for _ in range(3):
            for cell in cells:
                log("cell id: " + str(cell.id))
                bq.set_balance_cell(cell.id, True)
                util.clock.sleep(1000)
                bq.set_balance_cell(cell.id, False)
        log("Finished")

    def test_precharge(self):
        log("Testing Precharge Circuit")
        log("Use multimeter to measure current (mA) going into the pack.")
        log("Fully charged batteries will see little to no precharge current.")
        bq = self.controller.bq
        driver = self.controller.driver
        bq.charge(False)
        log("   Charge FET turned off")
        bq.discharge(True)
        log("   Discharge FET turned on")
        driver.precharge(True)
        log("   Precharge FET turned on")
        log("   Sleeping 10 seconds")
        util.clock.sleep(10000)
        driver.precharge(False)
        log("   Precharge FET turned off")
        bq.discharge(False)
        log("   Discharge FET turned off")
        log("Finished")

    def test_thermistors(self):
        log("Testing Thermistors")
        log("This test will print the temperature readings of Thermestor 1, 2 & 3 for 30 seconds.")
        log("Use a heat gun, or ice, or your hand to change the temperature of each Thermestor.")
        temps = self.controller.temps
        for _ in range(30):
            log("Therm #1: ", temps.read_temp1())
            log("Therm #2: ", temps.read_temp2())
            log("Therm #3: ", temps.read_temp3())
            util.clock.sleep(1000)






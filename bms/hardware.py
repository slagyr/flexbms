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

        bq.load_cell_voltages(cells)
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
        log("finished")





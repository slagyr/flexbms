from bms.states.machine import Statemachine
import bms.version as version

class Controller:
    def __init__(self, clock):
        self.tick_count = 0
        self.clock = clock
        self.logger = None
        self.serial = None
        self.bq = None
        self.driver = None
        self.cells = None
        self.temps = None
        self.pack = None
        self.rebooter = None

        self.sm = Statemachine(self)
        self._sm_tick_interval = 500
        self._last_sm_tick = 0
        self._screen_outdated = True
        self._has_alert = False
        self.alert_msg = None
        self.error_resume = False

    def setup(self):
        self.logger.setup()
        self.log("--------------------------------------")
        self.log("Setup Flex BMS version", version.name())
        self.log("--------------------------------------")

        self.sm.setup()
        self.bq.setup()
        self.driver.setup()
        self.cells.setup()

    def sm_tick_interval(self, millis=None):
        if millis is None:
            return self._sm_tick_interval
        else:
            self._sm_tick_interval = millis

    def screen_outdated(self, outdated=None):
        pass

    def handle_alert(self):
        self._has_alert = True

    # @clocked_fn
    def tick(self):
        my = self
        my.tick_count += 1
        millis = my.clock.millis()
        self.logger.tick(my.tick_count, millis)

        if my._has_alert:
            my._has_alert = False
            my.bq.process_alert()
            if my.bq.faults:
                my.sm.alert()

        tickless_millis = my.clock.millis_diff(millis, my._last_sm_tick)
        if tickless_millis >= my._sm_tick_interval:
            my.sm.tick()
            my._last_sm_tick = millis

        my.cells.expire()
        my.temps.expire()
        my.pack.expire()

    def loaded_cells(self):
        my = self
        my.cells.load()
        my.logger.cells(my.cells)
        my.serial.cells(my.cells)
        return my.cells

    def loaded_pack(self):
        my = self
        my.pack.load()
        my.logger.pack(my.pack)
        my.serial.pack(my.pack)
        return my.pack

    def loaded_temps(self):
        my = self
        my.temps.load()
        my.logger.temps(my.temps)
        my.serial.temps(my.temps)
        return my.temps

    def trigger_alert(self, msg):
        self.alert_msg = msg
        self.sm.alert()

    def log(self, *argv):
        self.logger.info(*argv)

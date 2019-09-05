# MicroPython compatible implementation of FlexBMS

from pyb import I2C
from pyb import Pin
from pyb import ADC
from pyb import ExtInt
from pyb import Timer
from pyb import USB_VCP
import utime
import gc
import sys

import machine
import bms.util
from bms.bq import *
from bms.conf import Config
from bms.controller import Controller
from bms.cells import Cells
from bms.driver import Driver
from bms.logger import Logger
from bms.serial import Serial
from bms.pack import Pack
from bms.rotary import Rotary

# For debugging Interrupts.  Allows memory to print error.
import micropython

from bms.temps import Temps

micropython.alloc_emergency_exception_buf(200)

TICK_INTERVAL = 250

class Rebooter:
    def reboot(self):
        machine.reset()

class Clock:
    def millis(self):
        return utime.ticks_ms()

    def millis_since(self, then):
        return utime.ticks_diff(utime.ticks_ms(), then)

    def millis_diff(self, after, before):
        return utime.ticks_diff(after, before)

    def millis_add(self, time, millis):
        return utime.ticks_add(time, millis)

    def sleep(self, millis):
        utime.sleep_ms(millis)


bms.util.clock = Clock()


class Debouncer:
    def __init__(self, pin, edge, timer_id, callback):
        self.callback = callback
        self.timer = Timer(timer_id)
        self.timer.init(freq=5)
        self.interrupt = ExtInt(pin, edge, Pin.PULL_NONE, self.start)
        self.end_cb = self.end

    def start(self, line):
        self.interrupt.disable()
        self.callback()
        self.timer.callback(self.end_cb)

    def end(self, timer):
        timer.callback(None)
        self.interrupt.enable()


class FlexBMS:
    def __init__(self):
        self.controller = None
        self.tick_interval = 500
        self.ok = True
        self.rot_rot_db = None
        self.rot_clk_db = None
        self._hardware = None
        self.alert_pim = None
        self.conf = None

    def init(self):
        self.conf = Config()
        self.conf.startup()
        self.controller = Controller(self.conf, bms.util.clock)
        logger = Logger()
        serial = Serial(self.controller, USB_VCP())
        i2c = I2C(1, I2C.MASTER, baudrate=100000)
        bq = BQ(self.conf, i2c)
        driver = Driver(Pin("Y8", Pin.OUT_PP, Pin.PULL_DOWN),
                        Pin("Y7", Pin.OUT_PP, Pin.PULL_DOWN),
                        Pin("Y6", Pin.OUT_PP, Pin.PULL_DOWN),
                        ADC(Pin("X11")))
        rotary = Rotary(Pin("X2", Pin.IN, Pin.PULL_UP), Pin("X1", Pin.IN, Pin.PULL_UP))
        cells = Cells(self.conf, bq, self.conf.CELL_SERIES)
        temps = Temps(bq)
        pack = Pack(bq, driver)

        self.controller.logger = logger
        self.controller.serial = serial
        self.controller.bq = bq
        self.controller.driver = driver
        self.controller.cells = cells
        self.controller.rotary = rotary
        self.controller.temps = temps
        self.controller.pack = pack
        self.controller.rebooter = Rebooter()

        rotary_button = Pin("X3", Pin.IN, Pin.PULL_UP)
        self.rot_rot_db = Debouncer(rotary.clk, ExtInt.IRQ_FALLING, 1, rotary.handle_rotate)
        self.rot_clk_db = Debouncer(rotary_button, ExtInt.IRQ_FALLING, 4, rotary.handle_click)

        self.alert_pin = Pin("X12", Pin.IN, Pin.PULL_UP)
        def alert_handler(line):
            self.controller.handle_alert()
        ExtInt(self.alert_pin, ExtInt.IRQ_RISING, Pin.PULL_NONE, alert_handler)

    def loop(self):
        while self.ok:
            before = utime.ticks_ms()
            try:
                self.controller.tick()
            except Exception as e:
                self.log_error(e)
                self.controller.error_resume = True
                self.controller.sm.error()
            tick_duration = utime.ticks_diff(utime.ticks_ms(), before)
            sleepytime = TICK_INTERVAL - tick_duration
            if sleepytime > 0:
                utime.sleep_ms(sleepytime)
            self.controller.serial.read()

    def log_error(self, e):
        with open("error.txt", "a") as f:
            sys.print_exception(e, f)
            f.flush()
        sys.print_exception(e)
        if self.controller and self.controller.logger:
            logger = self.controller.logger
            logger.error(str(e))
            sys.print_exception(e, logger.log)
        if self.controller and self.controller.serial:
            self.controller.serial.error(str(e))

    def main(self):
        try:
            self.init()
            self.controller.setup()
            self.controller.last_user_event_time = utime.ticks_ms()
        except Exception as e:
            self.log_error(e)
            return -1

        gc.collect()
        self.controller.logger.info("gc.mem_alloc(): " + str(gc.mem_alloc()))
        self.controller.logger.info("gc.mem_free():  " + str(gc.mem_free()))

        try:
            self.loop()
        except Exception as e:
            self.log_error(e)
            return -2

    def hardware(self):
        if self._hardware is None:
            from bms.hardware import Hardware
            self._hardware = Hardware(self.controller)
        return self._hardware



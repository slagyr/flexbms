# MicroPython compatible implementation of FlexBMS

import pyb
from pyb import I2C
from pyb import Pin
from pyb import ADC
from pyb import ExtInt
from pyb import Timer
import utime
import gc
import sys

import bms.util
from bms.bq import *
from bms.controller import Controller
from bms.cells import Cells
from bms.display import Display
from bms.driver import Driver
from bms.events import Events
from bms.rotary import Rotary

TICK_INTERVAL = 500


class Clock:
    def millis(self):
        return utime.ticks_ms()

    def millis_since(self, then):
        return utime.ticks_diff(utime.ticks_ms(), then)


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
        self.controller = Controller()
        self.tick_interval = 500
        self.ok = True
        self.rot_rot_db = None
        self.rot_clk_db = None

    def init(self):
        i2c = I2C(1, I2C.MASTER, baudrate=100000)
        bq = BQ(i2c)
        driver = Driver(Pin("Y8", Pin.OUT_PP),
                        Pin("Y7", Pin.OUT_PP),
                        Pin("Y6", Pin.OUT_PP),
                        ADC(Pin("X11")))
        display = Display(i2c)
        cells = Cells(CELL_COUNT)
        rotary = Rotary(Pin("X2", Pin.IN), Pin("X3", Pin.IN))
        events = Events(None)
        events.listeners.append(rotary)

        self.controller.display = display
        self.controller.bq = bq
        self.controller.driver = driver
        self.controller.cells = cells
        self.controller.rotary = rotary
        self.controller.events = events

        rotary_button = Pin("X1", Pin.IN)
        self.rot_rot_db = Debouncer(rotary.clk, ExtInt.IRQ_FALLING, 1, rotary.handle_rotate)
        self.rot_clk_db = Debouncer(rotary_button, ExtInt.IRQ_FALLING, 4, rotary.handle_click)

    def loop(self):
        while self.ok:
            before = utime.ticks_ms()
            self.controller.tick(before)
            tick_duration = utime.ticks_diff(utime.ticks_ms(), before)
            if tick_duration < TICK_INTERVAL:
                utime.sleep_ms(TICK_INTERVAL - tick_duration)

    def log_error(self, e):
        with open("error.txt", "a") as f:
            sys.print_exception(e, f)
            f.flush()
        sys.print_exception(e)

    def main(self):
        try:
            self.init()
            self.controller.setup()
            self.controller.last_user_event_time = utime.ticks_ms()
        except Exception as e:
            self.ok = False
            self.log_error(e)
            if self.controller:
                self.controller.set_screen(self.controller.error_screen)

        print("gc.mem_alloc(): " + str(gc.mem_alloc()))
        print("gc.mem_free():  " + str(gc.mem_free()))

        try:
            self.loop()
        except Exception as e:
            self.log_error(e)
            self.controller.set_screen(self.controller.error_screen)

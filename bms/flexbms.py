import board
import busio
import neopixel
import time
import rotaryio
import gamepad
import digitalio
import analogio
import gc
import sys

from bms.bq import *
from bms.controller import Controller
from bms.cells import Cells
from bms.display import Display
from bms.driver import Driver
from bms.events import Events
from bms.rotary import Rotary


def init():
    neopix = neopixel.NeoPixel(board.NEOPIXEL, 1)
    neopix[0] = (0, 0, 0)

    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    bq = BQ(i2c)
    driver = Driver(digitalio.DigitalInOut(board.D10),
                    digitalio.DigitalInOut(board.D11),
                    digitalio.DigitalInOut(board.D12),
                    analogio.AnalogIn(board.A0))
    display = Display(i2c)
    cells = Cells(CELL_COUNT)
    rotary = Rotary(rotaryio.IncrementalEncoder(board.D6, board.D5))
    events = Events(gamepad.GamePad(digitalio.DigitalInOut(board.D9)))
    events.listeners.append(rotary)

    controller = Controller()
    controller.display = display
    controller.bq = bq
    controller.driver = driver
    controller.cells = cells
    controller.rotary = rotary
    controller.events = events

    return controller


TICK_INTERVAL = 0.5
OK = True


def loop(controller):
    global OK
    while OK:
        before = time.monotonic()
        controller.tick(before)
        tick_duration = time.monotonic() - before
        if tick_duration < TICK_INTERVAL:
            time.sleep(TICK_INTERVAL - tick_duration)


def log_error(e):
    with open("/error.txt", "a") as f:
        sys.print_exception(e, f)
        f.flush()
    sys.print_exception(e)


def main():
    global OK
    controller = None
    try:
        controller = init()
        controller.setup()
    except Exception as e:
        OK = False
        log_error(e)
        if controller:
            controller.set_screen(controller.error_screen)

    print("gc.mem_alloc(): " + str(gc.mem_alloc()))
    print("gc.mem_free():  " + str(gc.mem_free()))

    try:
        loop(controller)
    except Exception as e:
        log_error(e)
        controller.set_screen(controller.error_screen)

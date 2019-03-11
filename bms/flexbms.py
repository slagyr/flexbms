import board
import busio
import neopixel
import time
import rotaryio
import gamepad
import digitalio
import gc

from bms.bq import *
from bms.controller import Controller
from bms.cells import Cells
from bms.display import Display
from bms.events import Events
from bms.rotary import Rotary


def init():
    neopix = neopixel.NeoPixel(board.NEOPIXEL, 1)
    neopix[0] = (0, 0, 0)

    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    bq = BQ(i2c)
    display = Display(i2c)
    cells = Cells(CELL_COUNT)
    rotary = Rotary(rotaryio.IncrementalEncoder(board.D6, board.D5))
    events = Events(gamepad.GamePad(digitalio.DigitalInOut(board.D9)))
    events.listeners.append(rotary)

    controller = Controller()
    controller.display = display
    controller.bq = bq
    controller.cells = cells
    controller.rotary = rotary
    controller.events = events

    return controller


TICK_INTERVAL = 0.5

def main():
    controller = init()
    controller.setup()

    print("gc.mem_alloc(): " + str(gc.mem_alloc()))
    print("gc.mem_free():  " + str(gc.mem_free()))

    while True:
        before = time.monotonic()
        controller.tick(time.monotonic())
        tick_duration = time.monotonic() - before
        if tick_duration < TICK_INTERVAL:
            time.sleep(TICK_INTERVAL - tick_duration)\


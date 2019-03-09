import board
import busio
import neopixel
import time

from bms.bq import *
from bms.controller import Controller
from bms.cells import Cells
from bms.display import Display


def init():
    neopix = neopixel.NeoPixel(board.NEOPIXEL, 1)
    neopix[0] = (0, 0, 0)

    # TODO - setup interrupts (ALERT, and buttons)

    controller = Controller()
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    bq = BQ(i2c)
    display = Display(i2c)
    cells = Cells(CELL_COUNT)

    controller.display = display
    controller.bq = bq
    controller.cells = cells
    return controller

TICK_INTERVAL = 0.5

def main():
    controller = init()

    controller.setup()

    while True:
        before = time.monotonic()
        controller.tick(time.monotonic())
        tick_duration = time.monotonic() - before
        if tick_duration < TICK_INTERVAL:
            time.sleep(TICK_INTERVAL - tick_duration)



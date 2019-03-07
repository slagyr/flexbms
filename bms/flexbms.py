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
    cells = Cells(bq, CELL_COUNT)

    controller.display = display
    controller.bq = bq
    controller.cells = cells
    return controller


def main():
    controller = init()

    controller.setup()

    while True:
        controller.tick(time.monotonic())
        time.sleep(0.25)



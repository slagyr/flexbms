import board
import busio
import gc
import neopixel
import time

from bms.ssd1306.display import Display
from bms.controller import Controller
from bms.bq76940 import BQ76940


def main():
    i2c = busio.I2C(board.SCL, board.SDA)

    neopix = neopixel.NeoPixel(board.NEOPIXEL, 1)
    neopix[0] = (0, 0, 0)

    # TODO - setup interrupts (ALERT, and buttons)

    display = Display(i2c)
    bq = BQ76940(i2c)
    controller = Controller()

    controller.display = display
    controller.bq = bq

    controller.setup()

    while True:
        controller.tick(time.monotonic())
        time.sleep(0.1)


def bq():
    i2c = busio.I2C(board.SCL, board.SDA)
    bq = BQ76940(i2c)
    return bq
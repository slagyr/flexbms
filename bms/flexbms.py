import board
import busio
import gc
import neopixel
import time

from bms.ssd1306.display import Display
from bms.controller import Controller
from bms.bq76940 import *


def init():
    neopix = neopixel.NeoPixel(board.NEOPIXEL, 1)
    neopix[0] = (0, 0, 0)

    # TODO - setup interrupts (ALERT, and buttons)

    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    bq = BQ76940(i2c)
    display = Display(i2c)
    controller = Controller()
    controller.display = display
    controller.bq = bq
    return controller


def main():
    controller = init()

    controller.setup()

    while True:
        controller.tick(time.monotonic())
        time.sleep(0.1)


def bq():
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    bq = BQ76940(i2c)
    return bq

def test():
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    bq = BQ76940(i2c)
    bq.write_register(CC_CFG, 0x19)
    while True:
        gain1 = bq.read_register_single(0x50)
        print("gain1: " + str(gain1))
        gain2 = bq.read_register_single(0x59)
        print("gain2: " + str(gain2))
        offset = bq.read_register_single(0x51)
        print("offset: " + str(offset))
        time.sleep(0.1)

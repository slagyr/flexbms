# MicroPython

import pyb
import sys
import utime

# if FS_MODE:
#     print("FS MODE.  Not booting")
#     led = pyb.LED(2)
#     while True:
#         led.toggle()
#         pyb.delay(125)
# else:
    # from flexbms_mpy import FlexBMS
    # bms = FlexBMS()
    # bms.main()

from pyb import Pin
from pyb import ADC
from pyb import I2C
from bms.display import Display
from bms.util import load_binary_into
import bms.fonts as fonts

OFFSET = 2.5
GAIN = 0.02512
#1194 = 30V : 0.025188916876574
#1592 = 40V : 0.025173064820642
#1996 = 50V : 0.02508780732564
# GAIN = gain = pack_v / (loaded_adc - offset)

log = open("volts.log", "a+")

apin = ADC(Pin("X11"))
i2c = I2C(1, I2C.MASTER, baudrate=100000)
display = Display(i2c)
display.font = fonts.font8x8()
display.inverted = False
display.setup()
load_binary_into("splash", display.buffer)
display.draw_text(60, 7, "Volts")
display.show()
utime.sleep_ms(1000)
start = utime.ticks_ms()

while True:
    sum = 0
    for i in range(10):
        adc = apin.read()
        sum += adc
    avg = sum / 10
    v = (avg - OFFSET) * GAIN
    # print(avg)
    print(v)
    log.write(str((utime.ticks_ms() - start) / 1000) + ": " + str(v) + "\n")
    log.flush()

    display.clear()
    display.draw_text(40, 3, "{} adc".format(avg))
    display.draw_text(40, 5, "{0:.2f} V".format(v))
    display.show()

    utime.sleep_ms(250)






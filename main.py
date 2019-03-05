# from bms import flexbms
#
# flexbms.main()

import gc

def mem_check(msg):
    print(str(msg) + ": " + str(gc.mem_free()))

from board import SCL, SDA
# mem_check("from board import SCL, SDA")
import busio
# mem_check("import busio")
import bms.ssd1306.screen
# mem_check("import bms.ssd1306.screen")
import bms.bin
# mem_check("import bms.bin")
import time
# mem_check("import time")

i2c = busio.I2C(SCL, SDA)
mem_check("i2c")
gc.collect()
mem_check("after gc")
screen = bms.ssd1306.screen.Screen(i2c)
mem_check("screen")
screen.setup()
mem_check("setup")
gc.collect()
mem_check("after gc")

splash = bms.bin.load("splash")
blank = bytearray(1024)
partial = bytearray(256)

gc.collect()

while True:

    t1 = time.monotonic()
    screen.clear()
    t2 = time.monotonic()
    print("clear        : " + str(t2 - t1))

    t1 = time.monotonic()
    screen.show()
    t2 = time.monotonic()
    print("show         : " + str(t2 - t1))

    t1 = time.monotonic()
    screen.draw_byxels(0, 0, 128, 8, splash)
    t2 = time.monotonic()
    print("draw splash b: " + str(t2 - t1))
    screen.show()

    t1 = time.monotonic()
    screen.draw_text(5, 2, "I'm a little teapot")
    screen.show()
    t2 = time.monotonic()
    print("draw_text    : " + str(t2 - t1))

    t1 = time.monotonic()
    screen.draw_byxels(32, 2, 64, 4, partial)
    t2 = time.monotonic()
    print("partial update: " + str(t2 - t1))
    screen.show()

    time.sleep(5)



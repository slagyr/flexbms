# from bms import flexbms
#
# flexbms.main()

from board import SCL, SDA
import busio
import bms.ssd1306.comm
import bms.ssd1306.screen
import bms.bin
import time

i2c = busio.I2C(SCL, SDA)
comm = bms.ssd1306.comm.Comm(i2c)
screen = bms.ssd1306.screen.Screen(comm)
screen.setup()
splash = bms.bin.load("splash")

while True:

    t1 = time.monotonic()
    screen.clear_screen()
    t2 = time.monotonic()
    print("clear_screen: " + str(t2 - t1))

    t1 = time.monotonic()
    screen.draw_byxels(0, 0, 128, 8, splash)
    t2 = time.monotonic()
    print("draw_bitmap: " + str(t2 - t1))

    t1 = time.monotonic()
    screen.draw_text(5, 2, "I'm a little teapot")
    t2 = time.monotonic()
    print("draw_string: " + str(t2 - t1))

    t1 = time.monotonic()
    screen.draw_bitmap(32, 2, 64, 32, bytearray(256))
    t2 = time.monotonic()
    print("partial update: " + str(t2 - t1))

    time.sleep(5)



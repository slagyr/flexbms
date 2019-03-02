# from bms import flexbms
#
# flexbms.main()

from board import SCL, SDA
import busio
from resources.bingen import splash
import bms.ssd1306.comm
import bms.ssd1306.screen

i2c = busio.I2C(SCL, SDA)
comm = bms.ssd1306.comm.Comm(i2c)
screen = bms.ssd1306.screen.Screen(comm)

screen.clear_screen()
screen.draw_bitmap(0, 0, 128, 64, splash.splashBMP)
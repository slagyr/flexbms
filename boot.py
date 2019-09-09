import pyb

FS_MODE = False

fspin = pyb.Pin("X5", pyb.Pin.IN, pyb.Pin.PULL_UP)
pressed = fspin.value() == 0

pyb.usb_mode('VCP+MSC')
# if pressed:
#     pyb.usb_mode('VCP+MSC')
#     FS_MODE = True
# else:
#     pyb.usb_mode('VCP')
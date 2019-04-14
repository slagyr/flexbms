import pyb

FS_MODE = False

fspin = pyb.Pin("Y9", pyb.Pin.IN)
pressed = fspin.value() == 0

if pressed:
    pyb.usb_mode('VCP+MSC')
    FS_MODE = True
else:
    pyb.usb_mode('VCP')
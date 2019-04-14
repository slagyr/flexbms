# MicroPython
import pyb

if FS_MODE:
    print("FS MODE.  Not booting")
    led = pyb.LED(2)
    while True:
        led.toggle()
        pyb.delay(125)
else:
    from flexbms_mpy import FlexBMS
    bms = FlexBMS()
    bms.main()





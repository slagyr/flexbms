import os

# CircuitPython
#ON_BOARD = os.uname()[0].startswith("samd")
# MicroPython
ON_BOARD = os.uname()[0] == "pyboard"

if not ON_BOARD:
    def const(v):
        return v
    # const() is micropython compiler feature that inlines values and avoids global lookups

# To be initialized by flexbms_x.py
clock = None

if not ON_BOARD:
    import time


    class Clock:
        def millis(self):
            return int(round(time.time() * 1000))

        def millis_since(self, then):
            now = int(round(time.time() * 1000))
            return now - then

        def millis_diff(self, after, before):
            return after - before

        def millis_after(self, time, millis):
            return time + millis

        def sleep(self, millis):
            time.sleep(millis / 1000)


    clock = Clock()

BIN_ROOT = "bms/bin/"


def file_readinto(f, buffer):
    if ON_BOARD:
        f.readinto(buffer)
    else:
        data = f.read()
        for i in range(len(data)):
            buffer[i] = data[i]


def load_binary(name):
    f = open(BIN_ROOT + name, 'rb')
    try:
        return f.read()
    finally:
        f.close()


def load_binary_into(name, buffer):
    f = open(BIN_ROOT + name, 'rb')
    try:
        file_readinto(f, buffer)
    finally:
        f.close()


log = print
if not ON_BOARD:
    def log(*args, **kwargs): pass


def clocked_fn(f, *args, **kwargs):
    myname = str(f).split(' ')[1]

    def new_func(*args, **kwargs):
        start = clock.millis()
        result = f(*args, **kwargs)
        delta = clock.millis_since(start)
        log('clocked_fn {} : {:n} ms'.format(myname, delta))
        return result

    return new_func


BYTEARRAY1 = bytearray(1)
BYTEARRAY2 = bytearray(2)
BYTEARRAY3 = bytearray(3)
BYTEARRAY4 = bytearray(4)


def bytearray1(a):
    BYTEARRAY1[0] = a
    return BYTEARRAY1


def bytearray2(a, b):
    BYTEARRAY2[0] = a
    BYTEARRAY2[1] = b
    return BYTEARRAY2


def bytearray3(a, b, c):
    BYTEARRAY3[0] = a
    BYTEARRAY3[1] = b
    BYTEARRAY3[2] = c
    return BYTEARRAY3


def bytearray4(a, b, c, d):
    BYTEARRAY4[0] = a
    BYTEARRAY4[1] = b
    BYTEARRAY4[2] = c
    BYTEARRAY4[3] = d
    return BYTEARRAY4

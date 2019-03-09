import time
import os

ON_BOARD = os.uname()[0].startswith("samd")

if not ON_BOARD:
    def const(v):
        return v
    # const() is micropython compiler feature that inlines values and avoids global lookups

BIN_ROOT = "bms/bin/"
BYTEARRAY1 = bytearray(1)
BYTEARRAY2 = bytearray(2)
BYTEARRAY3 = bytearray(3)
BYTEARRAY4 = bytearray(4)


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


def clocked_fn(f, *args, **kwargs):
    myname = str(f).split(' ')[1]

    def new_func(*args, **kwargs):
        start = time.monotonic()
        result = f(*args, **kwargs)
        delta = time.monotonic() - start
        print('clocked_fn {} : {:6.3f} s'.format(myname, delta))
        return result

    return new_func

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

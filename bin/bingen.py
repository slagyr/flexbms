#!/usr/bin/env python

import os

IN_DIR = 'resources/bingen/'
OUT_DIR = 'bms/bin/'

def read_bingen_file(filename):
    full_filename = IN_DIR + filename
    f = open(full_filename, "r")
    src = f.read()
    f.close()
    print(full_filename + ": " + str(len(src)))

    bytes = eval(src)
    print("\tbytes: " + str(len(bytes)))
    return bytes

def write_binary(filename, bytes):
    full_filename = OUT_DIR + filename
    print("writing to " + full_filename)
    f = open(OUT_DIR + filename[0:-3], "wb")
    f.write(bytes)
    f.close()

genfiles = os.listdir(IN_DIR)

for filename in genfiles:
    print(filename + " ------------------")
    bytes = read_bingen_file(filename)
    write_binary(filename, bytes)

BIN_ROOT = "bms/bin/"


def load(name):
    f = open(BIN_ROOT + name, 'rb')
    try:
        return f.read()
    finally:
        f.close()


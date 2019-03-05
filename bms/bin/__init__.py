from bms.stream import FileStream

BIN_ROOT = "bms/bin/"


def load(name):
    f = open(BIN_ROOT + name, 'rb')
    try:
        return f.read()
    finally:
        f.close()

def stream(name):
    return FileStream(BIN_ROOT + name)


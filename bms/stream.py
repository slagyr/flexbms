import os

class ByteStream:

    def __init__(self, bytes):
        self._bytes = bytes
        self._size = len(bytes)

    def bytes(self):
        return self._bytes

    def size(self):
        return len(self._bytes)

    def __enter__(self):
        self._i = -1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def next(self):
        self._i += 1
        if self._i >= self._size:
            raise IndexError("Stream ended")
        return self._bytes[self._i]

    def position(self):
        return self._i + 1


class FileStream:

    def __init__(self, filename):
        self._filename = filename
        st = os.stat(filename)
        if type(st) == tuple:    # circuitpython
            self._size = st[6]
        else:                    # python
            self._size = st.st_size

    def filename(self):
        return self._filename

    def size(self):
        return self._size

    def __enter__(self):
        self._i = 0
        self._file = open(self._filename, 'rb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()

    def next(self):
        b = self._file.read(1)
        if len(b) == 0:
            raise IndexError("Stream ended")
        self._i += 1
        return b[0]

    def position(self):
        return self._i


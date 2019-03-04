import unittest
import tempfile
from bms.stream import ByteStream, FileStream


class StreamTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_creating_bytestream(self):
        bytes = bytearray([1, 2, 3, 4, 5, 6])
        stream = ByteStream(bytes)
        self.assertEqual(bytes, stream.bytes())
        self.assertEqual(6, stream.size())

    def test_bytestream_implements_context_manager(self):
        with ByteStream(bytearray([1, 2, 3])) as stream:
            self.assertEqual(1, stream.next())
            self.assertEqual(2, stream.next())
            self.assertEqual(3, stream.next())

    def test_reading_past_end_of_bytestream(self):
        with ByteStream(bytearray([1, 2, 3])) as stream:
            stream.next()
            stream.next()
            stream.next()
            self.assertEqual(3, stream.position())
            try:
                stream.next()
                self.fail("should throw exeeption")
            except IndexError as e:
                self.assertEqual("Stream ended", e.args[0])


    def test_creating_filestream(self):
        filename = tempfile.gettempdir() + "/bms.tmp"
        with open(filename, "wb") as f:
            f.write(bytes([1, 2, 3]))

        stream = FileStream(filename)
        self.assertEqual(filename, stream.filename())
        self.assertEqual(3, stream.size())

    def test_filestream_implements_context_manager(self):
        filename = tempfile.gettempdir() + "/bms.tmp"
        with open(filename, "wb") as f:
            f.write(bytes([1, 2, 3]))

        with FileStream(filename) as stream:
            self.assertEqual(1, stream.next())
            self.assertEqual(2, stream.next())
            self.assertEqual(3, stream.next())

    def test_reading_past_end_of_filestream(self):

        filename = tempfile.gettempdir() + "/bms.tmp"
        with open(filename, "wb") as f:
            f.write(bytes([1, 2, 3]))

        with FileStream(filename) as stream:
            stream.next()
            stream.next()
            stream.next()
            self.assertEqual(3, stream.position())
            try:
                stream.next()
                self.fail("should throw exeeption")
            except IndexError as e:
                self.assertEqual("Stream ended", e.args[0])






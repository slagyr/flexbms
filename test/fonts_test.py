import unittest
import bms.fonts as fonts

class FontsTest(unittest.TestCase):

    def setUp(self):
        pass
        
    def test_no_fonts_loaded_initally(self):
        fonts.clear()
        self.assertEqual(None, fonts._font5x7)
        self.assertEqual(None, fonts._font6x8)
        self.assertEqual(None, fonts._font8x8)

    def test_loading_5x7(self):
        f = fonts.font5x7()
        self.assertIsNotNone(f)
        self.assertIsInstance(f, bytes)
        self.assertIs(f, fonts.font5x7())

    def test_loading_6x8(self):
        f = fonts.font6x8()
        self.assertIsNotNone(f)
        self.assertIsInstance(f, bytes)
        self.assertIs(f, fonts.font6x8())

    def test_loading_8x8(self):
        f = fonts.font8x8()
        self.assertIsNotNone(f)
        self.assertIsInstance(f, bytes)
        self.assertIs(f, fonts.font8x8())
import unittest

from bms.events import Events


class MockButtons(object):
    def __init__(self):
        self.pressed = 0

    def get_pressed(self):
        return self.pressed

class ButtonListener:
    def __init__(self):
        self.press_count = 0
        self.release_count = 0

    def pressed(self):
        self.press_count += 1

    def released(self):
        self.release_count += 1


class EventsTest(unittest.TestCase):

    def setUp(self):
        self.buttons = MockButtons()
        self.events = Events(self.buttons)
        self.foo = ButtonListener()
        self.bar = ButtonListener()

    def test_creation(self):
        self.assertEqual(self.buttons, self.events.buttons)

    def test_dispatch_single(self):
        self.events.listeners.append(self.foo)

        self.buttons.pressed = 0b10 # second button only
        self.events.dispatch()
        self.buttons.pressed = 0b00  # second button only
        self.events.dispatch()
        self.assertEqual(0, self.foo.press_count)
        self.assertEqual(0, self.foo.release_count)

        self.buttons.pressed = 0b01 # first button
        self.events.dispatch()
        self.assertEqual(1, self.foo.press_count)
        self.buttons.pressed = 0b00 # first button
        self.events.dispatch()
        self.assertEqual(1, self.foo.release_count)

    def test_dispatch_multiple(self):
        self.events.listeners.append(self.foo)
        self.events.listeners.append(self.bar)

        self.buttons.pressed = 0b10 # second button only
        self.events.dispatch()
        self.assertEqual(0, self.foo.press_count)
        self.assertEqual(0, self.foo.release_count)
        self.assertEqual(1, self.bar.press_count)
        self.assertEqual(0, self.bar.release_count)

        self.buttons.pressed = 0b01 # first button
        self.events.dispatch()
        self.assertEqual(1, self.foo.press_count)
        self.assertEqual(0, self.foo.release_count)
        self.assertEqual(1, self.bar.press_count)
        self.assertEqual(1, self.bar.release_count)

        self.buttons.pressed = 0b11 # first button
        self.events.dispatch()
        self.assertEqual(1, self.foo.press_count)
        self.assertEqual(0, self.foo.release_count)
        self.assertEqual(2, self.bar.press_count)
        self.assertEqual(1, self.bar.release_count)


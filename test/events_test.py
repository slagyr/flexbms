import unittest

from bms.events import Events


class MockButtons(object):
    def __init__(self):
        self.pressed = 0

    def get_pressed(self):
        return self.pressed


class EventsTest(unittest.TestCase):

    def setUp(self):
        self.buttons = MockButtons()
        self.events = Events(self.buttons)
        self.bauble = ""

    def foo(self):
        self.bauble += "foo"

    def bar(self):
        self.bauble += "bar"

    def test_creation(self):
        self.assertEqual(self.buttons, self.events.buttons)

    def test_dispatch_single(self):
        self.events.dispatchers.append(self.foo)

        self.buttons.pressed = 0b10 # second button only
        self.events.dispatch()
        self.assertEqual("", self.bauble)

        self.buttons.pressed = 0b01 # first button
        self.events.dispatch()
        self.assertEqual("foo", self.bauble)

    def test_dispatch_multiple(self):
        self.events.dispatchers.append(self.foo)
        self.events.dispatchers.append(self.bar)

        self.buttons.pressed = 0b10 # second button only
        self.events.dispatch()
        self.assertEqual("bar", self.bauble)

        self.buttons.pressed = 0b01 # first button
        self.events.dispatch()
        self.assertEqual("barfoo", self.bauble)

        self.buttons.pressed = 0b11 # first button
        self.events.dispatch()
        self.assertEqual("barfoofoobar", self.bauble)


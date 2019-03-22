import unittest

from bms import fonts
from bms.screens.menu import Menu
from test.mock_controller import MockController

class MockMenuItem:
    def __init__(self, name):
        self.name = name
        self.was_selected = False

    def menu_name(self):
        return self.name

    def menu_sel(self):
        self.was_selected = True


class MenuTest(unittest.TestCase):

    def setUp(self):
        self.controller = MockController()
        self.display = self.controller.display
        self.rotary = self.controller.rotary
        self.menu = Menu(self.controller, "Main")
        self.first = MockMenuItem("first")
        self.second = MockMenuItem("second")
        self.third = MockMenuItem("third")
        self.menu.add(self.first)
        self.menu.add(self.second)
        self.menu.add(self.third)

    def test_sets_font(self):
        self.menu.enter()
        self.assertEqual(fonts.font6x8(), self.controller.display.font)

    def test_title(self):
        self.assertEqual("Main", self.menu.title)

    def test_add_item(self):
        self.assertEqual(self.first, self.menu.items[0])
        self.assertEqual(self.second, self.menu.items[1])
        self.assertEqual(self.third, self.menu.items[2])

    def test_first_item_highlighted_on_enter(self):
        self.menu.enter()
        self.assertEqual(0, self.menu.highlighted)
        self.assertEqual(True, self.display.was_shown)

    def test_rotary_click_selects_item(self):
        self.menu.enter()
        self.rotary.clicked = True
        self.menu.user_input()

        self.assertEqual(True, self.first.was_selected)
        
    def test_rotary_position_changed_highlighted(self):
        self.menu.enter()
        self.display.was_shown = False
        self.rotary.rel_pos = 1
        self.menu.user_input()

        self.assertEqual(True, self.controller.screen_outdated())
        self.assertEqual(1, self.menu.highlighted)

    def test_highlighted_stays_within_bounds(self):
        self.menu.enter()
        self.rotary.rel_pos = -1
        self.menu.user_input()
        self.assertEqual(0, self.menu.highlighted)

        self.rotary.rel_pos = 10
        self.menu.user_input()
        self.assertEqual(2, self.menu.highlighted)

    def test_bug_were_previous_doesnt_get_unhighlighted(self):
        self.menu.enter()
        self.rotary.rel_pos = 1
        self.display.drawn_text = []

        self.menu.user_input()
        self.menu.update()

        # self.display.print_buffer()
        self.assertEqual("1) first", self.display.drawn_text[0][0])
        self.assertEqual("2) second", self.display.drawn_text[1][0])






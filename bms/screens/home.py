# Abstract class for screens that can be set as home screen
class HomeScreen:
    def __init__(self, controller):
        self.controller = controller
        self.idle_timeout = None

    def user_input(self):
        if self.controller.rotary.clicked:
            self.controller.set_screen(self.controller.main_menu)

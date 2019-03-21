class State:
    def __init__(self, sm):
        self.sm = sm

    def enter(self):
        pass

    def exit(self):
        pass

    def tick(self, millis):
        raise RuntimeError("Unimplemented event 'tick' in " + str(self.__class__.__name__))

    def low_v(self):
        raise RuntimeError("Unimplemented event 'low_v' in " + str(self.__class__.__name__))

    def norm_v(self):
        raise RuntimeError("Unimplemented event 'norm_v' in " + str(self.__class__.__name__))

    def pow_on(self):
        raise RuntimeError("Unimplemented event 'pow_on' in " + str(self.__class__.__name__))

    def pow_off(self):
        raise RuntimeError("Unimplemented event 'pow_off' in " + str(self.__class__.__name__))

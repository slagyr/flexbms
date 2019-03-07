import atexit
import sys

all_mocks = []

@atexit.register
def find_bad_mocks():
    bad = 0
    for mock in all_mocks:
        r = mock.are_you_a_good_little_mock()
        if not r:
            bad += 1
    if bad > 0:
        raise RuntimeError("Some naughty mocks spoiled the run.")

class Mock:

    mock_check_performed = False

    def __new__(cls, *args, **kwargs):
        m = super(Mock, cls).__new__(cls)
        all_mocks.append(m)
        return m

    def assert_mock(self, idol):
        self.mock_check_performed = True
        needs = set(dir(idol))
        has = set(dir(self))
        missing = needs.difference(has)
        if len(missing) > 0:
            raise RuntimeError("Tsk, Tsk.  Poor mocking job.  Missing stuff: " + str(missing))

    def are_you_a_good_little_mock(self):
        if not self.mock_check_performed:
            print("assert_mock must be called at the end of __init__: " + str(type(self)), file = sys.stderr)
            return False
        else:
            return True

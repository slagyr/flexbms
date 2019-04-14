from bms.util import ON_BOARD, log


def _parse(s):
    if s == "True":
        return True
    elif s == "False":
        return False
    elif s[0] == "'":
        return s[1::-1]
    elif "." in s:
        return float(s)
    else:
        return int(s)


class Config:
    def __init__(self):
        self.CELL_SERIES = 10
        self.CELL_PARALLEL = 1
        self.CELL_MAX_V = 4.2
        self.CELL_MIN_V = 2.5
        self.CELL_MAX_CHG_I = 1.5
        self.CELL_MAX_DSG_I = 10

        self.BALANCE_ENABLED = True
        self.BALANCE_THRESH = 0.01

        self.BQ_CRC_ATTEMPTS = 5
        self.BQ_RSNS = 1
        self.BQ_SCD_DELAY = 0x1  # 100us
        self.BQ_SCD_THRESH = 0x2  # 89mV
        self.BQ_OCD_DELAY = 0x3  # 80ms
        self.BQ_OCD_THRESH = 0x8  # 61mV
        self.BQ_UV_DELAY = 0x2  # 0x0: 1s, 0x1:4s, 0x2: 8s, 0x3: 16s
        self.BQ_OV_DELAY = 0x1  # 0x0: 1s, 0x1:2s, 0x2: 4s, 0x3: 8s

        self.PACK_V_TOLERANCE = 0.5
        self.PACK_V_OFFSET = 0
        self.PACK_V_GAIN = 0.017496341463415
        self.PACK_I_TOLERANCE = 0.05

        self.TEMP_MAX_PACK_CHG = 45
        self.TEMP_MIN_PACK_CHG = 0
        self.TEMP_MAX_PACK_DSG = 60
        self.TEMP_MIN_PACK_DSG = -20

    def save(self):
        with open(CONF_FILE, "w") as f:
            for field in sorted(self.__dict__.keys()):
                value = self.__dict__[field]
                line = field + ": " + str(value) + "\n"
                f.write(line)

    def load(self):
        with open(CONF_FILE, "r") as f:
            line = f.readline()
            while line:
                tokens = line.split(":", 1)
                field = tokens[0]
                value = _parse(tokens[1].strip())
                setattr(self, field, value)
                line = f.readline()

    def startup(self):
        try:
            self.load()
        except Exception as e:
            log("Failed to load config file.  Rewriting it.")
            log(e)
            self.save()

    def reset(self):
        new = Config()
        for f in new.__dict__:
            v = getattr(new, f)
            setattr(self, f, v)


# cells in parallel
# max charge current
# cell voltage threshold for determining full or empty
# balance duration (already above as BALANCE_INTERVAL)
# balance rest duration
# charger:battery V threshold to determine if charger is plugged in
# amperage threshold to turn on CHG FET in normal state
# normal state interval for checking cell voltages
# threshold for acceptable charger voltage


CONF = Config()
if ON_BOARD:
    CONF_FILE = "bms.conf"
else:
    import tempfile
    CONF_FILE = tempfile.gettempdir() + "/bms_test.conf"



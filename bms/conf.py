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
        self.CELL_COUNT = 10
        self.CELL_MAX_V = 4.2
        self.CELL_MIN_V = 2.5

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

    def save(self):
        with open(CONF_FILE, "w") as f:
            for field in self.__dict__:
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
        except RuntimeError:
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
CONF_FILE = "bms.conf"


# TODO - Load from a config file
# TODO - Make it saveable to config file
# TODO - Store in an instance object so tests dont interfere

CELL_COUNT = 10
CELL_MAX_V = 4.2
CELL_MIN_V = 2.5

BALANCE_THRESH = 0.01
BALANCE_ENABLED = True
BALANCE_INTERVAL = 60000 # 1 min

BQ_CRC_ATTEMPTS = 5
BQ_RSNS = 1
BQ_SCD_DELAY = 0x1  # 100us
BQ_SCD_THRESH = 0x2  # 89mV
BQ_OCD_DELAY = 0x3  # 80ms
BQ_OCD_THRESH = 0x8  # 61mV
BQ_UV_DELAY = 0x2 # 0x0: 1s, 0x1:4s, 0x2: 8s, 0x3: 16s
BQ_OV_DELAY = 0x1 # 0x0: 1s, 0x1:2s, 0x2: 4s, 0x3: 8s

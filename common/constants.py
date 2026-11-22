import numpy as np

# BOARD_TIMESTEPS = 3
# BOARD_CHANNELS = 2
# COL_DICT = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
# WTHOR_COORDINATE_LEN = 2
BOARD_SIZE = 8
BLANK_CELL = 0
OWN_CELL = 1
STOLEN_CELL = -1
ACTION_SIZE = 65
PASS_ACTION = 64
BOARD_DTYPE = np.dtype(np.int8)
BLACK = 0
WHITE = 1
import math
from common.constants import *

def id2position(id):
    row = id // BOARD_SIZE
    col = id % BOARD_SIZE
    
    return (row, col)

def position2id(position):
    action_row, action_col = position
    return action_row * BOARD_SIZE + action_col

def get_state_key(state):
    if state.dtype != BOARD_DTYPE:
        raise ValueError(f"dtypeが異なります。dtype : {state.dtype}")
    
    if state.shape != (2, BOARD_SIZE, BOARD_SIZE):
        raise ValueError(f"shapeが異なります。shape : {state.shape}")
    
    # stateのメモリ配置がスライスや転置等でずれていた場合は隣り合うように変換する
    return np.ascontiguousarray(state).tobytes()


def valid_gamma(gamma):
    if (0 > gamma or gamma > 1) or not math.isfinite(gamma):
        raise ValueError("割引率には0~1の値を設定してください。")
    
def valid_alpha(alpha):
    if (0 > alpha or alpha > 1) or not math.isfinite(alpha):
        raise ValueError("alphaには0~1の値を設定してください。")
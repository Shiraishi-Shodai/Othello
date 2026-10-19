from enum import Enum
from utils import SquarePosition

WRITE_SQUARE                 = 1     # 白石
BLACK_SQUARE                 = 2     # 黒石
BLANK_SQUARE                 = 0     # 空マス
OTHELLO_BOARD_SIZE           = 8     # 盤面のサイズ
INIT_SQUARE_POSITION_FROM_START = 3  # 盤面初期化時に石を置く位置(前から添え字を数える用)
INIT_SQUARE_POSITION_FROM_END   = 4  # 盤面初期化時に石を置く位置(後ろから添え字を数える用)
TURN_OVER_NUM_ZERO              = 0  # ひっくり返せるマスが　0マス

class SearchDirectionOffsets(Enum):
    # (row, col)
    ABOVE_SQUARE_POSITION       = SquarePosition(-1, 0)  # 上
    ABOVE_RIGHT_SQUARE_POSITION = SquarePosition(-1, 1)  # 右上
    RIGHT_SQUARE_POSITION       = SquarePosition(0, 1)   # 右
    BELOW_RIGHT_SQUARE_POSITION = SquarePosition(1, 1)   # 右下
    BELOW_SQUARE_POSITION       = SquarePosition(1, 0)   # 下
    BELOW_LEFT_SQUARE_POSITION  = SquarePosition(1, -1)  # 左下
    LEFT_SQUARE_POSITION        = SquarePosition(0, -1)  # 左
    ABOVE_LEFT_SQUARE_POSITION  = SquarePosition(-1, -1) # 左上
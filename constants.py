from enum import Enum

WRITE_SQUARE                 = 1   # 白石
BLACK_SQUARE                 = 2   # 黒石
BLANK_SQUARE                 = 0   # 空マス
OTHELLO_BOARD_SIZE           = 8   # 盤面のサイズ
INIT_SQUARE_INDEX_FROM_START = 3   # 盤面初期化時に石を置く位置(前から添え字を数える用)
INIT_SQUARE_INDEX_FROM_END   = 4   # 盤面初期化時に石を置く位置(後ろから添え字を数える用)

class SearchDirectionIndexes(Enum):
    # (row, col)
    ABOVE_SQUARE_INDEX       = (-1, 0)  # 上
    ABOVE_RIGHT_SQUARE_INDEX = (-1, 1)  # 右上
    RIGHT_SQUARE_INDEX       = (0, 1)   # 右
    BELOW_RIGHT_SQUARE_INDEX = (1, 1)   # 右下
    BELOW_SQUARE_INDEX       = (1, 0)   # 下
    BELOW_LEFT_SQUARE_INDEX  = (1, -1)  # 左下
    LEFT_SQUARE_INDEX        = (0, -1)  # 左
    ABOVE_LEFT_SQUARE_INDEX  = (-1, -1) # 左上
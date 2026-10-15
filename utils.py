import constants
from dataclasses import dataclass
import torch

@dataclass(slots=True)
class SquarePosition:
    row: int
    col: int
    

def move_square_position(target_square_position: SquarePosition, offset_square_position: SquarePosition):
    """
    マスの位置をずらす
    sample: 右斜め前にずらす(3, 3) = SquarePosition(2, 3) + SquarePosition(1, 1)
    SquarePositionのオブジェクトがこの関数が呼ばれるたびに生成されることを防ぐために、rowとcolのみ返す
    """
    moved_square_row = 0
    moved_square_col = 0
    
    moved_square_row = target_square_position.row + offset_square_position.row
    moved_square_col = target_square_position.col + offset_square_position.col
    
    return moved_square_row, moved_square_col

def validate_board_position(target_square_position: SquarePosition, output_assert=False):
    """指定したマスが盤面外か判定
    """
    assert isinstance(target_square_position, SquarePosition), f"データ型が異なります: {target_square_position, type(target_square_position)}"

    if (target_square_position.row in torch.arange(constants.OTHELLO_BOARD_SIZE)) and (target_square_position.col in torch.arange(constants.OTHELLO_BOARD_SIZE)):
        return True
    
    if output_assert:
        assert True, f"無効なマス: {target_square_position}が指定されました。"

    return False
    
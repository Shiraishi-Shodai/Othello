import constants
from dataclasses import dataclass
import torch
from itertools import cycle

@dataclass(slots=True)
class SquarePosition:
    row: int
    col: int
    
@dataclass(slots=True)
class DirectionalTurnOverInfo:
    """単一方向にオセロをひっくり返すための情報
    """
    direction                   : constants.SearchDirectionOffsets # オセロをひっくり返す方向
    bracketing_player_position  : SquarePosition                   # 相手マスを挟むプレイヤーマスの位置
    turn_over_num               : int                              # ひっくり返せる相手マスの枚数

@dataclass(slots=True)
class MoveTurnOverInfo:
    """全方向にオセロをひっくり返すための情報
    """
    legal_move_position         : SquarePosition                  # 着手位置
    directional_turn_over_infos : list[DirectionalTurnOverInfo]   # 着手位置から見て各方向ごとのオセロをひっくり返すための情報
    
    def __str__(self):
        lines = [
            f"=======着手位置: {self.legal_move_position}=======",
            f"着手位置{self.legal_move_position}でオセロをひっくり返す際に使用する情報"
        ]
        
        for directional_turn_over_info in self.directional_turn_over_infos:
            lines.append(
                # f"  オセロをひっくり返す方向 : {directional_turn_over_info.direction.name}\n"
        #         f"  相手マスを挟むプレイヤーマスの位置 : {directional_turn_over_info.bracketing_player_position}\n"
                f"  ひっくり返せる相手マスの枚数 : {directional_turn_over_info.turn_over_num}\n"
            )
        
        return "\n".join(lines)


def move_square_position(target_square_position: SquarePosition, offset_square_position: SquarePosition) -> tuple:
    """
    マスの位置をずらす
    sample: 右斜め前にずらす(3, 3) = SquarePosition(2, 3) + SquarePosition(1, 1)
    SquarePositionのオブジェクトがこの関数が呼ばれるたびに生成されることを防ぐために、rowとcolのみ返す
    """
    
    return (target_square_position.row + offset_square_position.row, 
            target_square_position.col + offset_square_position.col)

def validate_board_position(target_square_position: SquarePosition, assert_output=False):
    """指定したマスが盤面外か判定
    """
    assert isinstance(target_square_position, SquarePosition), f"データ型が異なります: {target_square_position, type(target_square_position)}"

    if (target_square_position.row in torch.arange(constants.OTHELLO_BOARD_SIZE)) and (target_square_position.col in torch.arange(constants.OTHELLO_BOARD_SIZE)):
        return True
    
    if assert_output:
        assert True, f"無効なマス: {target_square_position}が指定されました。"

    return False

def player_switcher(players: list):
    for player in cycle(players):
        yield player
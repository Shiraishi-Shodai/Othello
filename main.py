import torch
import constants
from utils import move_square_position, SquarePosition, validate_board_position, DirectionalTurnOverInfo, MoveTurnOverInfo
class OthelloEnvironment:
    def __init__(self):
        self.square_type = torch.int8
        self.reset_board()
    
    def reset_board(self):
        # 全マスを空マスにする
        self.board = torch.zeros((constants.OTHELLO_BOARD_SIZE, constants.OTHELLO_BOARD_SIZE), dtype=self.square_type)
        # 白マスを初期位置に置く
        self.board[constants.INIT_SQUARE_POSITION_FROM_START, constants.INIT_SQUARE_POSITION_FROM_START] = constants.WRITE_SQUARE
        self.board[-constants.INIT_SQUARE_POSITION_FROM_END, -constants.INIT_SQUARE_POSITION_FROM_END] = constants.WRITE_SQUARE
        # 黒マスを初期位置に置く
        self.board[constants.INIT_SQUARE_POSITION_FROM_START, -constants.INIT_SQUARE_POSITION_FROM_END] = constants.BLACK_SQUARE
        self.board[-constants.INIT_SQUARE_POSITION_FROM_END, constants.INIT_SQUARE_POSITION_FROM_START] = constants.BLACK_SQUARE
    
    def _filter_blank_square_positions(self) -> list[SquarePosition]:
        """ (row, col)のlist[tuple]形式でブランクマスのpositionを返す
        """
        
        # ブランクマスの行・列のインデックスを取得する
        # before : self.board
        # after  : (torch.tensor([0, 0, 1]), torch.tensor([2, 3, 0]))
        blank_square_indices : tuple[torch.Tensor, ...] = torch.where(self.board == constants.BLANK_SQUARE)

        # ブランクマスなしの時
        if blank_square_indices[0].numel() == 0:
            return []

        # 行・列のインデックスを、マスごとの座標に変換する
        # before : (torch.tensor([0, 0, 1]), torch.tensor([2, 3, 0]))
        # after  : tensor([[0, 2], [0, 3], [1, 0]])
        blank_square_coordinates : torch.Tensor = torch.stack(blank_square_indices, dim=1).to(dtype=self.square_type)
       
        # 座標を SquarePosition に変換する
        # before : tensor([[0, 2], [0, 3], [1, 0]])
        # after  : [SquarePosition(row=0, col=2), SquarePosition(row=0, col=3), SquarePosition(row=1, col=0)]
        blank_square_positions : list[SquarePosition] = list(map(lambda x : SquarePosition(x[0], x[1]), 
                                                                 blank_square_coordinates.tolist())) 
        
        return blank_square_positions

    def _find_move_turn_over_infos(self, 
                                   player_square        : int, 
                                   opponent_square      : int, 
                                   blank_square_position: SquarePosition) -> MoveTurnOverInfo:
        """渡されたターゲットマスの場所を基準に8方向を探索し、反転できるマスが1つ以上あるマスとそのマスで相手マスをひっくり返すための付属情報を返す
        """
        move_turn_over_infos = MoveTurnOverInfo(blank_square_position, [])
        
        # 各ブランクマスを対象に着手可能なマスを取得
        for search_direction_offset in constants.SearchDirectionOffsets:
            unidirectional_turn_over_info = self._find_unidirectional_turn_over_info(player_square, 
                                                                                     opponent_square, 
                                                                                     blank_square_position, 
                                                                                     search_direction_offset)
            
            
            if unidirectional_turn_over_info is None:
                continue
            
            move_turn_over_infos.directional_turn_over_infos.append(unidirectional_turn_over_info)
        
        return move_turn_over_infos
    
    def _find_unidirectional_turn_over_info(self, 
                                            player_square                 : int, 
                                            opponent_square               : int,
                                            blank_square_position         : SquarePosition,
                                            search_direction_offset : constants.SearchDirectionOffsets) -> DirectionalTurnOverInfo | None:
        # マスを進める基準となるマス
        next_square_position = SquarePosition(blank_square_position.row, blank_square_position.col)
        next_square = self.board[next_square_position.row, next_square_position.col].item()
        assert next_square == constants.BLANK_SQUARE, f"指定されたマスはブランクマスではありません。{next_square_position}, {next_square}"
        
        turn_over_num = 0
        
        while True:
            # ある方向に1つマスを動かす
            next_square_row, next_square_col = move_square_position(next_square_position, search_direction_offset.value)
            next_square_position.row = next_square_row
            next_square_position.col = next_square_col
            
            # 動かした先がボードの外であれば、着手不可
            if not validate_board_position(next_square_position):
                return None
            
            next_square = self.board[next_square_position.row, next_square_position.col].item()
            
            # 着手可否を検証するブランクマスから1つずらしたマスがプレイヤーマスなら着手不可
            if turn_over_num == constants.TURN_OVER_NUM_ZERO and next_square == player_square:
                return None
            
            # マスを進めた先がブランクなら着手可否を検証するブランクマスには着手不可
            if next_square == constants.BLANK_SQUARE:
                return None
            
            # マスを進めた先が相手マス
            if next_square == opponent_square:
                # ひっくり返せるマス数をインクリメント
                turn_over_num += 1
                continue
            
            # プレイヤーの石とプレイヤーの石で相手プレイヤーの石を挟めればOK
            if next_square == player_square:
                unidirectional_turn_over_info = DirectionalTurnOverInfo(
                    direction=search_direction_offset,
                    bracketing_player_position=SquarePosition(
                        row=next_square_position.row, 
                        col=next_square_position.col
                        ),
                    turn_over_num=turn_over_num
                    )
                return unidirectional_turn_over_info
            
            # 想定外の場合(無限ループを防ぐため)
            return None
            
            

    def compute_legal_move_infos(self, 
                                 player_square   : int, 
                                 opponent_square : int) -> list[MoveTurnOverInfo]:
        """着手できるマスを計算し、対象のマスをすべて返す
        sample: {
                    # 着手可能マス
                    SquarePosition(row=3, col=3): {
                        legal_move_position
                        (
                            UnidirectionalTurnOverInfo(
                                SquarePosition(row=5, col=3),  # 相手マスを挟むプレイヤーマスの位置
                                SquarePosition(row=1, col=0),  # オセロをひっくり返す方向
                                2                              # ある方向にひっくり返せる相手マスの枚数
                            ),
                            UnidirectionalTurnOverInfo(
                                SquarePosition(row=5, col=3),  # 相手マスを挟むプレイヤーマスの位置
                                SquarePosition(row=-1, col=0), # オセロをひっくり返す方向
                                2                              # ある方向にひっくり返せる相手マスの枚数
                            ),
                        ),
                    },
                    SquarePosition(row=5, col=1): {
                        # 別の着手位置に対する反転情報
                        ...
                    },
                }
        """
        
        legal_move_infos: list[MoveTurnOverInfo] = []
        # ブランクマスの位置を取得
        blank_square_positions = self._filter_blank_square_positions()
        
        if not blank_square_positions:
            return legal_move_infos

        # 各ブランクマスを対象に着手可能なマスを取得
        for blank_square_position in blank_square_positions:
            move_turn_over_infos = self._find_move_turn_over_infos(player_square=player_square, 
                                                                   opponent_square=opponent_square, 
                                                                   blank_square_position=blank_square_position)
            
            # # ひっくり返せるマスがない → 着手不可
            if not move_turn_over_infos.directional_turn_over_infos:
                continue
            
            legal_move_infos.append(move_turn_over_infos)
        
        return legal_move_infos
    
    def is_game_over(self) -> bool:
        blank_square_num = self.board[self.board == constants.BLANK_SQUARE].numel()
        if blank_square_num:
            return True
        
        return False
        
class Player:
    def __init__(self, play_square):
        self.play_square = play_square
    
    
def temp():
    pass
    
def main():
    # 盤面の初期化
    othello_env = OthelloEnvironment()    
    # プレイヤーとコンピュータの先行・後攻決め
    
    # おけるマスの取得
    legal_move_infos : list[MoveTurnOverInfo] = othello_env.compute_legal_move_infos(1, 2)
    for i in legal_move_infos:
        print(i)
    
    # パスの判定
    if not legal_move_infos:
        print("着手可能なマスがありません。パスします。")

    # オセロを置く
    
    # マスをひっくり返す
    
    # ゲーム終了の判定
    if othello_env.is_game_over():
        print("ゲーム終了")
    
    # 次の着手を行う

if __name__ == "__main__":
    temp()
    main()
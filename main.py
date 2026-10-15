import torch
import constants
from utils import move_square_position, SquarePosition, validate_board_position
class OthelloEnvironment:
    def __init__(self):
        self.reset_board()
    
    def reset_board(self):
        # 全マスを空マスにする
        self.board = torch.zeros((constants.OTHELLO_BOARD_SIZE, constants.OTHELLO_BOARD_SIZE), dtype=torch.int8)
        # 白マスを初期位置に置く
        self.board[constants.INIT_SQUARE_INDEX_FROM_START, constants.INIT_SQUARE_INDEX_FROM_START] = constants.WRITE_SQUARE
        self.board[-constants.INIT_SQUARE_INDEX_FROM_END, -constants.INIT_SQUARE_INDEX_FROM_END] = constants.WRITE_SQUARE
        # 黒マスを初期位置に置く
        self.board[constants.INIT_SQUARE_INDEX_FROM_START, -constants.INIT_SQUARE_INDEX_FROM_END] = constants.BLACK_SQUARE
        self.board[-constants.INIT_SQUARE_INDEX_FROM_END, constants.INIT_SQUARE_INDEX_FROM_START] = constants.BLACK_SQUARE
    
    def _filter_blank_square_positions(self):
        """ (row, col)のlist[tuple]形式でブランクマスのpositionを返す
        """
        blank_square_positions = torch.where(self.board == constants.BLANK_SQUARE) # (torch.tensor([0, 0, 1]), torch.tensor([2, 3, 0]))
        # ブランクマスなしの時
        if blank_square_positions[0].numel() == 0:
            return []

        blank_square_positions = torch.stack(blank_square_positions, dim=1)          # tensor([[0, 2], [0, 3], [1, 0]])
        # [SquarePosition(row=0, col=2), SquarePosition(row=0, col=3), SquarePosition(row=1, col=0)]
        blank_square_positions = list(map(lambda x : SquarePosition(x[0], x[1]), blank_square_positions.tolist()))   
        
        return blank_square_positions

    def _canMove(self, player_square: int, opponent_square: int, blank_square_position: SquarePosition):
        """渡されたターゲットマスの場所を基準に8方向を探索し、プレイヤーの石を着手可能か判断            
        """
        for search_direction_offset in constants.SearchDirectionOffsets:
            if self._can_capture(player_square, opponent_square, blank_square_position, search_direction_offset.value):
                return True
        
        return False
    
    def _can_capture(self, player_square, opponent_square, blank_square_position, search_direction_offset_value):
        # ブランクマスからある方向に1つ動かす
        next_square_position = SquarePosition(blank_square_position.row, blank_square_position.col)
        next_square_row, next_square_col = move_square_position(next_square_position, search_direction_offset_value)
        next_square_position.row = next_square_row
        next_square_position.col = next_square_col
        
        if not validate_board_position(next_square_position):
                return False
                
        # ターゲットを基準にある方向に1つマスを進めた場所が相手マスでないなら引数で受け取ったブランクマスには着手不可
        if self.board[next_square_position.row, next_square_position.col].item() != opponent_square:
                return False
                
        while True:
            # ある方向に1つマスを動かす
            next_square_row, next_square_col = move_square_position(next_square_position, search_direction_offset_value)
            next_square_position.row = next_square_row
            next_square_position.col = next_square_col
            if not validate_board_position(next_square_position):
                return False
            
            # マスを進めた先がブランクなら引数で受け取ったブランクマスには着手不可
            if self.board[next_square_position.row, next_square_position.col].item() == constants.BLANK_SQUARE:
                return False

            # プレイヤーの石とプレイヤーの石で相手プレイヤーの石を挟めればOK
            if self.board[next_square_position.row, next_square_position.col].item() == player_square:
                return True

    def compute_legal_move_positions(self, player_square, opponent_square):
        """着手できるマスを計算し、対象のマスをすべて返す
        """
        
        legal_move_positions = []
        blank_square_positions = self._filter_blank_square_positions()
        
        if not blank_square_positions:
            return legal_move_positions

        for blank_square_position in blank_square_positions:
            if self._canMove(player_square=player_square, opponent_square=opponent_square, blank_square_position=blank_square_position):
                legal_move_positions.append(blank_square_position)
        
        return legal_move_positions
        
class Player:
    def __init__(self, play_square):
        self.play_square = play_square
    
    

def main():
    # 盤面の初期化
    othello_env = OthelloEnvironment()    
    # プレイヤーとコンピュータの先行・後攻決め
    
    # おけるマスの取得
    legal_move_positions = othello_env.compute_legal_move_positions(1, 2)
    for i in legal_move_positions:
        print(i.row, i.col)

    # マスを置く
    
    # マスをひっくり返す
    
    # ゲーム終了の判定
    
    # パスの判定
    
    # 次の着手を行う

if __name__ == "__main__":
    main()
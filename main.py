import torch
import constants

class OthelloEnvironment:
    def __init__(self):
        self.reset_board()
    
    def reset_board(self):
        # 全マスを空マスにする
        self.board = torch.zeros((constants.OTHELLO_BOARD_SIZE, constants.OTHELLO_BOARD_SIZE))
        # 白マスを初期位置に置く
        self.board[constants.INIT_SQUARE_INDEX_FROM_START, constants.INIT_SQUARE_INDEX_FROM_START] = constants.WRITE_SQUARE
        self.board[-constants.INIT_SQUARE_INDEX_FROM_END, -constants.INIT_SQUARE_INDEX_FROM_END] = constants.WRITE_SQUARE
        # 黒マスを初期位置に置く
        self.board[constants.INIT_SQUARE_INDEX_FROM_START, -constants.INIT_SQUARE_INDEX_FROM_END] = constants.BLACK_SQUARE
        self.board[-constants.INIT_SQUARE_INDEX_FROM_END, constants.INIT_SQUARE_INDEX_FROM_START] = constants.BLACK_SQUARE
    
    def compute_legal_moves(self, player_square):
        blank_square_indexes = self._filter_blank_square_indexes()
    
    def _filter_blank_square_indexes(self):
        """ (row, col)のlist[tuple]形式でブランクマスのindexを返す
        """
        blank_square_indexes = torch.where(self.board == constants.BLANK_SQUARE) # (torch.tensor([0, 0, 1]), torch.tensor([2, 3, 0]))
        blank_square_indexes = torch.stack(blank_square_indexes, dim=1)          # tensor([[0, 2], [0, 3], [1, 0]])
        blank_square_indexes = list(map(tuple, blank_square_indexes.tolist()))   # [(0, 2), (0, 3), (1, 0)]
        
        return blank_square_indexes

    def _canMove(self, player_square, target_square_index):
        """渡されたターゲットマスの場所を基準に8方向を探索し、プレイヤーの石を着手可能か判断            
        """
        for search_direction_index in constants.SearchDirectionIndexes:
            # タプル要素ごとの足し算
            # sample: (2, 5) = (-1, 1) + (3, 4)
            search_index = tuple(t + s for t, s in zip(target_square_index, search_direction_index.value))
            
            # ターゲットを基準にある方向に1つマスを進めた場所がブランクなら、そこには石をおけない
            if self.board[search_index] == constants.BLANK_SQUARE:
                continue
            
            # ターゲットを基準にある方向に1つマスを進めた場所がプレイヤーの石なら、そこには石をおけない
            if self.board[search_index] == player_square:
                continue
            
            return True
        
        return False
        
class Player:
    def __init__(self, play_square):
        self.play_square = play_square
    
    

def main():
    # 盤面の初期化
    othello_env = OthelloEnvironment()
    
    # プレイヤーとコンピュータの先行・後攻決め
    
    # おけるマスの取得
    othello_env.compute_legal_moves(1)
    othello_env._canMove(1, (10, 10))
    
    
    # マスを置く
    
    # マスをひっくり返す
    
    # ゲーム終了の判定
    
    # パスの判定
    
    # 次の着手を行う

if __name__ == "__main__":
    main()
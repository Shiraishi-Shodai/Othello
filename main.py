import torch
import constants
from utils import move_square_position, SquarePosition, validate_board_position, DirectionalTurnOverInfo, MoveTurnOverInfo, player_switcher
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
    
    def _compute_turn_over_indices(self, 
                  legal_move_info : MoveTurnOverInfo, 
                  opponent_square : int,
                  ) -> torch.Tensor:
        """ユーザーが指定したマスを基準にひっくり返すボードの(row, col)のTensorを返す
        """
        legal_move_position = legal_move_info.legal_move_position
        
        # 着手マスの位置検証(指定したマス位置がボードの外であれば着手不可)
        validate_board_position(legal_move_position, assert_output=True)
        # 着手マスの値取得
        legal_move_square = self.board[legal_move_position.row, legal_move_position.col]
        # 着手マスの値検証(指定したマスがブランクマスでなければ着手不可)
        assert legal_move_square == constants.BLANK_SQUARE, f"指定されたマスは、相手マスでないため着手できません。\n指定マス位置: {legal_move_position}\n: 指定マスの値: {legal_move_square}"
        
        turn_over_indices : list[tuple] = []
        turn_over_position : SquarePosition = SquarePosition(row=legal_move_position.row, 
                                                             col=legal_move_position.col)

        turn_over_indices.append((legal_move_position.row, legal_move_position.col))
        
        for directional_turn_over_info in legal_move_info.directional_turn_over_infos:
            turn_over_position.row = legal_move_position.row
            turn_over_position.col = legal_move_position.col
            
            for _ in range(directional_turn_over_info.turn_over_num):
                
                # ひっくり返すマスの位置取得
                turn_over_row, turn_over_col = move_square_position(turn_over_position, directional_turn_over_info.direction.value)
                turn_over_position.row = turn_over_row
                turn_over_position.col = turn_over_col
                # ひっくり返すマスの位置検証(指定したマス位置がボードの外であれば着手不可)
                validate_board_position(turn_over_position, assert_output=True)

                turn_over_indices.append((turn_over_position.row, turn_over_position.col))

        return torch.tensor(turn_over_indices, dtype=torch.long)

    def step(self, 
            legal_move_info : MoveTurnOverInfo, 
            player_square: int,
            opponent_square : int
            ) -> None:
        
        turn_over_indices : torch.Tensor = self._compute_turn_over_indices(legal_move_info=legal_move_info, 
                                                                                        opponent_square=opponent_square)
        self.board[turn_over_indices[:, 0],turn_over_indices[:, 1]] = player_square

    def is_game_over(self) -> bool:
        blank_square_num = self.board[self.board == constants.BLANK_SQUARE].numel()
        
        if blank_square_num == constants.GAME_OVER_BLANK_NUM:
            return True
        
        return False
class Player:
    def __init__(self, player_square, opponent_square):
        self.player_square   = player_square
        self.opponent_square = opponent_square
        
    def get_action(self, len_legal_move_infos):
        action = 0
        while True:
            try:
                action = int(input(f"0 ~ {len_legal_move_infos - 1}までの数字を入力してください : "))
                
                # if 0 > action or action >= len_legal_move_infos:
                #     raise ValueError("指定した範囲の数字を入力してください")
                            
                break
            except:
                print("エラーを検知しました。もう一度入力してください")
                
        return action
    
    
def temp():
    # a = torch.arange(10).reshape(-1, 2)
    # b = torch.tensor([(0, 1), (2, 1), (4, 0)])
    # print(a, end="\n")
    # print(a[b[:, 0], b[:, 1]])
    
    a = SquarePosition(1, 0)
    b = [copy(a.row), copy(a.col)]
    print(b)
    a.row = 10
    a.col = 20
    
    print(b)
    
    pass
    
def main():
    # 盤面とプレイヤー初期化
    env      = OthelloEnvironment()   
    player1  = Player(player_square=constants.WRITE_SQUARE, opponent_square=constants.BLACK_SQUARE)
    player2  = Player(player_square=constants.BLACK_SQUARE, opponent_square=constants.WRITE_SQUARE)
    players  = [player1, player2]
    switcher = player_switcher(players)

    # プレイヤーとコンピュータの先行・後攻決め
    print(env.board, end="\n\n")
    
    while True:
        player = next(switcher)
        
        # 着手できる全マスとそのマスの付属情報を取得
        legal_move_infos : list[MoveTurnOverInfo] = env.compute_legal_move_infos(player_square=player.player_square,
                                                                                 opponent_square=player.opponent_square)
        for i in legal_move_infos:
            print(i)
        
        # パスの判定
        if not legal_move_infos:
            print("着手可能なマスがありません。パスします。")

        # 着手マスを指定
        action = player.get_action(len(legal_move_infos))
        
        if action == 100:
            break
        
        # ボードにオセロを置く
        env.step(legal_move_info=legal_move_infos[action], 
                player_square=player.player_square, 
                opponent_square=player.opponent_square)
        
        print(env.board, end="\n\n")
        
        # ゲーム終了の判定
        if env.is_game_over():
            print("ゲーム終了")
            break
        
if __name__ == "__main__":
    # temp()
    main()
import pandas as pd
import numpy as np
from typing import TypeAlias

BOARD_TIMESTEPS = 3
BOARD_CHANNELS = 2
BOARD_SIZE = 8
COL_DICT = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
ENV_ACTIONS  : TypeAlias = tuple[int, int] | None
MODEL_ACTIONS: TypeAlias = int
WTHOR_COORDINATE_LEN = 2
BLANK_CELL = 0
OWN_CELL = 1
STOLEN_CELL = -1

# 環境用のAction作成
def coordinate2action_id(coordinate) -> ENV_ACTIONS:
    """"f5" → (4, 5)
    """
    assert len(coordinate) == WTHOR_COORDINATE_LEN, f"渡された座標{coordinate}が正しくありません"

    col, row = coordinate[0], coordinate[1]
    col = COL_DICT[col]
    row = int(row) - 1
    return tuple((row, col))
    
def record2actions(record) -> np.ndarray[ENV_ACTIONS]:
    
    # [f5, d6, c5] → (4, 5), (5, 3), (4, 2)
    coordinates = [record[i : i + WTHOR_COORDINATE_LEN] for i in range(0, len(record), WTHOR_COORDINATE_LEN)]
    actions = np.array(list(map(lambda coordinate: coordinate2action_id(coordinate), coordinates)))
    return actions

def mak_all_game_actions(records):
    """読み込んだ全試合のデータを使って、1行1手のデータを作る
    """
    df = pd.DataFrame(columns=["game", "action"])
    for game, record in enumerate(records):
        assert len(record) % WTHOR_COORDINATE_LEN == 0, f"渡された棋譜{record}が正しくありません"
        index = int(len(record) / WTHOR_COORDINATE_LEN)
        
        action_df = pd.DataFrame(columns=["game", "action"],
                                 index=range(index))
        game += 1
        actions = record2actions(record)
        
        action_df["game"] = game
        action_df["action"] = actions
        df = pd.concat([df, action_df], ignore_index=True)
    
    return df
    
class Othello:
    def __init__(self):
        # 盤面の初期化
        self.state = np.zeros((2, BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
        self.player_turn = np.random.choice([True, False], p=[0.5, 0.5])
        
        self.init_index = {
            "Black": np.array([(3, 4), (4, 3)]),
            "White": np.array([(3, 3), (4, 4)])
        }
        
        self.directions = [
            (-1, 0),  # 上
            (-1, 1),  # 右上
            (0, 1),   # 右
            (1, 1),   # 右下
            (1, 0),   # 下
            (1, -1),  # 左下
            (0, -1),  # 左
            (-1, -1)  # 左上
        ]
         
        player_init_index = None
        opponent_init_index = None
        
        if self.player_turn:
            player_init_index = self.init_index["Black"]
            opponent_init_index = self.init_index["White"]
        else:
            player_init_index = self.init_index["White"]
            opponent_init_index = self.init_index["Black"]  
        
        self.state[0, player_init_index[:, 0], player_init_index[:, 1]] = OWN_CELL
        self.state[1, opponent_init_index[:, 0], opponent_init_index[:, 1]] = OWN_CELL

    
    def legal_mask(self, state):
        player_state, opponent_state = state[0], state[1]

        
    def states(self):
        pass
        
    def next_state(self, state, action):
        
        # パスの場合はそのまま返す
        if action is None:
            return state
        
        action_row, action_col = action
        player_state, opponent_state = state

        if not self._validate_index(action_row, action_col):
            raise ValueError("indexが不正です")
        
        if player_state[action_row, action_col] != BLANK_CELL or opponent_state[action_row, action_col] != BLANK_CELL:
            raise ValueError("ブランクでないマスが選択されました")

        self.calc_flippable_index(player_state, opponent_state, action_row, action_col)
        
        
    
    def _validate_index(self, row, col):
        if 0 > row or row >= BOARD_SIZE or 0 > col or col >= BOARD_SIZE:
            return False
        return True
    
    def _get_edge_index(self, start_row, start_col, direction_row, direction_col):
        # 探索方向の1番端を取得
        edge_row = start_row + (BOARD_SIZE - 1 - start_row) * direction_row
        edge_col = start_col + (BOARD_SIZE - 1 - start_col) * direction_col
        
        return (edge_row, edge_col)
    
    def calc_flippable_index(self, player_state, opponent_state, action_row, action_col):
        # ひっくり返せるマスのindexを取得する
        flippable_index = []

        state_mask = None
        if self.player_turn:
            state_mask = player_state - opponent_state
        else:
            state_mask = opponent_state - player_state
        
        for direction_row, direction_col in self.directions:

            next_row = action_row + direction_row
            next_col = action_col + direction_col
            
            if not self._validate_index(next_row, next_col):
                break
            
            next_cell = state_mask[next_row, next_col]

            # 1つ隣の石が現在のプレイヤーから見て相手マスでない
            if next_cell != STOLEN_CELL:
                break
            
            edge_row, edge_col = self._get_edge_index(action_row, action_col, direction_row, direction_col)
            
            # 現在のプレイヤーの石で相手石を挟むためのスペースがない
            if next_row == edge_row and next_col == edge_col:
                break
            
            # 探索方向の1番端までの石の一覧を取得
            search_rows = np.array(list(range(next_row + 1, edge_row + 1))).reshape(-1, 1)
            search_cols = np.array(list(range(next_col + 1, edge_col + 1))).reshape(-1, 1)
            search_index = np.concatenate((search_rows, search_cols))
            print(search_index)
            # search_cells = state_mask[]
        
            break  
                
        

    def step(self, action):
        pass


def main():

    csv_file = r"output.csv"
    wthor = pd.read_csv(csv_file)
    records = wthor["Record"].to_numpy()
    # mak_all_game_actions(records)
    
    env = Othello()
    env.player_turn = True
    action = (5, 4) # (5, 3)
    state = env.state
    env.next_state(state, action)
    

def tmp():
    a = list(range(10))
    print(a)

if __name__ == "__main__":
    main()
    tmp()
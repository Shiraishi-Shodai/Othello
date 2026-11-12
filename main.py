import pandas as pd
import numpy as np
from typing import TypeAlias
import itertools

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
MAX_INDEX = BOARD_SIZE - 1
MIN_INDEX = 0

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
        
        self.player_turn = True
        if self.player_turn:
            player_init_index = self.init_index["Black"]
            opponent_init_index = self.init_index["White"]
        else:
            player_init_index = self.init_index["White"]
            opponent_init_index = self.init_index["Black"]  
        
        self.state[0, player_init_index[:, 0], player_init_index[:, 1]] = OWN_CELL
        self.state[1, opponent_init_index[:, 0], opponent_init_index[:, 1]] = OWN_CELL

    
    def compute_legal_mask(self, state):
        blank_indexes = self._get_blank_indexes()
        legal_mask = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.bool)
        
        for blank_index in blank_indexes:
            action = tuple(map(int, blank_index))
            if not self._is_flippable(state, action):
                continue
            
            action_row, action_col = action
            legal_mask[action_row, action_col] = True
        
        return legal_mask

        
    def states(self):
        pass
        
    def next_state(self, state, action):
        
        # パスの場合はそのまま返す
        if action is None:
            return state
        
        next_state = state.copy()

        if not self._validate_index(action):
            raise ValueError("indexが不正です")
        
        # actionで選んだインデックスに石を置く
        action_row, action_col = action
        
        # アクションが合法手に含まれない
        legal_mask = self.compute_legal_mask(state)
        if not legal_mask[action_row, action_col]:
            return state

        if self.player_turn:
            next_state[0, action_row, action_col] = OWN_CELL
        else:
            next_state[1, action_row, action_col] = OWN_CELL

        # 石の反転
        # パターンa : 元々自分の石→相手にひっくり返された (1 → 0)
        # パターンb : 元々相手の石→ひっくり返した        (0 → 1)
        flippable_indexes = self._calc_flippable_indexes(state, action)
        next_state[:, flippable_indexes[:, 0], flippable_indexes[:, 1]] = 1 - state[:, flippable_indexes[:, 0], flippable_indexes[:, 1]]
        
        return next_state
    
    def _validate_index(self, action):
        action_row, action_col = action
        if 0 > action_row or action_row >= BOARD_SIZE or 0 > action_col or action_col >= BOARD_SIZE:
            return False
        return True
    
    def _get_blank_indexes(self):
        player_state, opponent_state = self.state
        blank_cell_rows, blank_cell_cols = np.where(1 - player_state - opponent_state != BLANK_CELL)
        blank_cell_rows = blank_cell_rows.reshape(-1, 1)
        blank_cell_cols = blank_cell_cols.reshape(-1, 1)
        blank_indexes = np.concatenate((blank_cell_rows, blank_cell_cols), axis=1)
        return blank_indexes

    def _is_flippable(self, state, action):
        flippable_indexes = self._calc_flippable_indexes(state, action)
        if len(flippable_indexes):
            return True
        
        return False
    
    def _calc_flippable_indexes(self, state, action):
        # ひっくり返せるマスのindexを取得する
        flippable_indexes = []
        action_row, action_col = action
        player_state, opponent_state = state

        # 現在のプレイヤー視点を統一(自分のマスは1, 相手のマスは-1とする)
        state_mask = None
        if self.player_turn:
            state_mask = player_state + opponent_state * -1
        else:
            state_mask = player_state * -1 + opponent_state
        
        for direction_row, direction_col in self.directions:
            flippable_index = []
            next_row = action_row
            next_col = action_col
            
            while True:
                next_row += direction_row
                next_col += direction_col
                
                if not self._validate_index((next_row, next_col)):
                    break
                
                next_cell = state_mask[next_row, next_col].item()

                if next_cell is BLANK_CELL:
                    break
                
                if next_cell is OWN_CELL:
                    flippable_indexes.append(flippable_index)
                    break
                
                flippable_index.append((next_row, next_col))
        
        flippable_indexes = np.array(list(itertools.chain.from_iterable(flippable_indexes))).reshape(-1, 2)
        return flippable_indexes
                

    def step(self, action):
        pass


def main():

    # csv_file = r"output.csv"
    # wthor = pd.read_csv(csv_file)
    # records = wthor["Record"].to_numpy()
    
    env = Othello()
    action = (5, 4)
    state = env.state
    next_state = env.next_state(state, action)
    

def tmp():
    pass


if __name__ == "__main__":
    main()
    # tmp()
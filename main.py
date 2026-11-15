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
ACTION_SIZE = 65
PASS_ACTION = 64

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
    
def id2position(id):
    row = id // BOARD_SIZE
    col = id % BOARD_SIZE
    
    return (row, col)

def position2id(position):
    action_row, action_col = position
    return action_row * BOARD_SIZE + action_col
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
            
    def states(self):
        pass
        
    def next_state(self, state, action):
        next_state = state.copy()
        
        # パスの場合はそのまま返す
        if action is PASS_ACTION:
            return next_state
        
        action_row, action_col = id2position(action)
        if not self._validate_index(action_row, action_col):
            raise ValueError("indexが不正です")
                
        # actionが合法手に含まれない
        legal_actions = self.compute_legal_actions(state)
        if action not in legal_actions:
            return next_state
        
        next_state = self.flip(state, action)
        
        return next_state

    def compute_legal_actions(self, state):
        blank_actions = self._get_blank_actions()
        legal_actions = []
        
        for blank_action in blank_actions:
            if not self._is_flippable(state, blank_action):
                continue

            legal_actions.append(blank_action)
        
        # 合法手がない場合は、パスとする
        if not legal_actions:
            legal_actions.append(PASS_ACTION)

        return legal_actions
    
    def flip(self, state, action):
        # 石の反転
        # パターンa : 元々自分の石→相手にひっくり返された (1 → 0)
        # パターンb : 元々相手の石→ひっくり返した        (0 → 1)
        next_state = state.copy()
        action_row, action_col = id2position(action)
        if self.player_turn:
            next_state[0, action_row, action_col] = OWN_CELL
        else:
            next_state[1, action_row, action_col] = OWN_CELL 
        flippable_indexes = self._calc_flippable_indexes(state, action)
        next_state[:, flippable_indexes[:, 0], flippable_indexes[:, 1]] = 1 - state[:, flippable_indexes[:, 0], flippable_indexes[:, 1]]
        return next_state
    
    def _validate_index(self, action_row, action_col):
        if action_row < 0 or action_row >= BOARD_SIZE or action_col < 0 or action_col >= BOARD_SIZE:
            return False
        return True
    
    def _get_blank_actions(self):
        player_state, opponent_state = self.state
        blank_cell_rows, blank_cell_cols = np.where(1 - player_state - opponent_state != BLANK_CELL)
        blank_cell_rows = blank_cell_rows
        blank_cell_cols = blank_cell_cols
        blank_actions = [position2id((int(row), int(col))) for row, col in zip(blank_cell_rows, blank_cell_cols)]
        return blank_actions

    def _is_flippable(self, state, action):
        flippable_indexes = self._calc_flippable_indexes(state, action)
        if len(flippable_indexes):
            return True
        
        return False
    
    def _calc_flippable_indexes(self, state, action):
        # ひっくり返せるマスのindexを取得する
        flippable_indexes = []
        action_row, action_col = id2position(action)
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
                
                if not self._validate_index(next_row, next_col):
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
    action = 37
    state = env.state
    next_state = env.next_state(state, action)
    print(next_state)

def tmp():
    a = np.zeros(16, dtype=np.bool)
    if True not in a:
        a[-1] = True
    print(a)

if __name__ == "__main__":
    main()
    # tmp()
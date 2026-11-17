import pandas as pd
import numpy as np
from typing import TypeAlias
import itertools
from copy import deepcopy

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
        self.state[0, 3, 4] = OWN_CELL
        self.state[0, 4, 3] = OWN_CELL
        self.state[1, 3, 3] = OWN_CELL
        self.state[1, 4, 4] = OWN_CELL
        
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
        
        self.legal_actions = []
        
            
    def states(self):
        pass
        
    def next_state(self, state, action, legal_actions, legal_mask):
        next_state = deepcopy(state)
        done = False
        
        # パスの場合はそのまま返す
        if action == PASS_ACTION:
            if not legal_mask[PASS_ACTION]:
                raise ValueError("Passは選択できません")
        else:
            action_row, action_col = id2position(action)
            if not self._validate_index(action_row, action_col):
                raise ValueError("indexが不正です")
                    
            # actionが合法手に含まれない
            if action not in legal_actions:
                raise ValueError(f"{action}は合法手ではありません")
            
            next_state = self.flip(state, action)
            
        # 終了判定
        done = self.is_done(next_state)
        
        # プレイヤー視点入れ替え(参照を持つビューではなく、独立した配列を生成するためにcopyを使用)
        next_state = next_state[::-1].copy()

        return next_state, done

    def compute_legal_actions(self, state):
        blank_actions = self._get_blank_actions(state)
        legal_actions = []
        
        for blank_action in blank_actions:
            if not self._is_flippable(state, blank_action):
                continue

            legal_actions.append(blank_action)
        
        # 合法手がない場合は、パスのみを選択可能な行動とする
        if not legal_actions:
            legal_actions.append(PASS_ACTION)
            
        return legal_actions
    
    def create_legal_mask(self, legal_actions):
        legal_mask = np.zeros(BOARD_SIZE*BOARD_SIZE, dtype=np.bool)
        legal_mask[legal_actions] = True
        return legal_mask.reshape(BOARD_SIZE, BOARD_SIZE)
    
    def flip(self, state, action):
        next_state = deepcopy(state)
        action_row, action_col = id2position(action)
        
        flippable_all_positions = self._calc_flippable_positions(state, action)
        flippable_rows, flippable_cols = flippable_all_positions[:, 0], flippable_all_positions[:, 1]
        
        if not len(flippable_all_positions):
            return next_state
        
        # 着手
        next_state[0, action_row, action_col] = OWN_CELL
        # 反転できる石を反転
        # パターンa : 元々自分の石→相手にひっくり返された (1 → 0)
        # パターンb : 元々相手の石→ひっくり返した        (0 → 1)
        next_state[:, flippable_rows, flippable_cols] = 1 - state[:, flippable_rows, flippable_cols]
        return next_state
    
    def is_done(self, next_state):
        # 終了条件1: 盤面がすべて埋まった
        sum_board = np.sum(next_state, axis=0)
        if np.all(sum_board == OWN_CELL).item():
            return True
        
        # 終了条件2: 2人も合法手が存在しない
        legal_actions_len = sum([len(self.compute_legal_actions(next_state[::turn])) for turn in [1, -1]])
        if not legal_actions_len:
            return True
        
        # それ以外はゲーム進行中
        return False
    
    def _validate_index(self, action_row, action_col):
        if action_row < 0 or action_row >= BOARD_SIZE or action_col < 0 or action_col >= BOARD_SIZE:
            return False
        return True
    
    def _get_blank_actions(self, state):
        player_state, opponent_state = state
        blank_cell_rows, blank_cell_cols = np.where(1 - player_state - opponent_state != BLANK_CELL)
        blank_cell_rows = blank_cell_rows
        blank_cell_cols = blank_cell_cols
        blank_actions = [position2id((int(row), int(col))) for row, col in zip(blank_cell_rows, blank_cell_cols)]
        return blank_actions

    def _is_flippable(self, state, action):
        flippable_all_positions = self._calc_flippable_positions(state, action)
        if len(flippable_all_positions):
            return True
        
        return False
    
    def _calc_flippable_positions(self, state, action):
        # ひっくり返せるマスのindexを取得する
        flippable_all_positions = []
        action_row, action_col = id2position(action)

        # 現在のプレイヤー視点を統一(自分のマスは1, 相手のマスは-1とする)
        state_mask = state[0] - state[1]
        
        for direction_row, direction_col in self.directions:
            flippable_positions = []
            next_row = action_row
            next_col = action_col
            
            while True:
                next_row += direction_row
                next_col += direction_col
                
                if not self._validate_index(next_row, next_col):
                    break

                next_cell = state_mask[next_row, next_col].item()

                if next_cell == BLANK_CELL:
                    break
                
                if next_cell == STOLEN_CELL:
                    flippable_positions.append([next_row, next_col])
                    continue
                
                if len(flippable_positions):
                    flippable_all_positions.extend(flippable_positions)
                break

        if not flippable_all_positions:
            return flippable_all_positions
        
        flippable_all_positions = np.array(flippable_all_positions).reshape(-1, 2)

        return flippable_all_positions
                

    def step(self, action):
        pass


def main():

    # csv_file = r"output.csv"
    # wthor = pd.read_csv(csv_file)
    # records = wthor["Record"].to_numpy()
    
    env = Othello()
    action = 0
    surrender_action = 100
    state = env.state

    while True:
        legal_actions = env.compute_legal_actions(state)
        legal_mask = env.create_legal_mask(legal_actions)
        # action = int(input(f"legal actions : {legal_actions}"))
        action = np.random.choice(legal_actions).item()
        if action == surrender_action:
            print("降参です")
            break
        next_state, done = env.next_state(state, action, legal_actions, legal_mask)
        state = next_state
        if done:
            break

    print(state.sum(axis=0))

if __name__ == "__main__":
    main()
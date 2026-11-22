import numpy as np
from collections import defaultdict
import math

# BOARD_TIMESTEPS = 3
# BOARD_CHANNELS = 2
# COL_DICT = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
# WTHOR_COORDINATE_LEN = 2
BOARD_SIZE = 8
BLANK_CELL = 0
OWN_CELL = 1
STOLEN_CELL = -1
ACTION_SIZE = 65
PASS_ACTION = 64
BOARD_DTYPE = np.dtype(np.int8)
# TODO : 勝敗の判定
COMPLETE = "complete"
DRAW     = "draw"
PROGRESS = "progress"
REWARD_DICT = {
    COMPLETE : 1,  # 盤面にすべて石を置いた状態である = 勝敗が決まった
    DRAW     : 0,  # 引き分け
    PROGRESS : 0   # ゲーム進行中
}

def id2position(id):
    row = id // BOARD_SIZE
    col = id % BOARD_SIZE
    
    return (row, col)

def position2id(position):
    action_row, action_col = position
    return action_row * BOARD_SIZE + action_col
class Othello:
    DIRECTIONS = [
        (-1, 0),  # 上
        (-1, 1),  # 右上
        (0, 1),   # 右
        (1, 1),   # 右下
        (1, 0),   # 下
        (1, -1),  # 左下
        (0, -1),  # 左
        (-1, -1)  # 左上
    ]    
        
    def __init__(self):
        # 盤面の初期化
        self.state = np.zeros((2, BOARD_SIZE, BOARD_SIZE), dtype=BOARD_DTYPE)
        self.state[0, 3, 4] = OWN_CELL
        self.state[0, 4, 3] = OWN_CELL
        self.state[1, 3, 3] = OWN_CELL
        self.state[1, 4, 4] = OWN_CELL
        
        self.start_state = self.state.copy()
        self.agent_state = self.state.copy()
        
    def reset(self):
        self.agent_state = self.start_state.copy()
        return self.agent_state

    def states(self):
        pass

    def next_state(self, state, action, legal_actions):
        next_state = state
                
        # actionが合法手に含まれない
        if action not in legal_actions:
            raise ValueError(f"{action}は合法手ではありません")
        
        # パスの場合はそのまま返す
        if action == PASS_ACTION:
            # パス以外の合法手が存在するにも関わらず、パスを選択した場合は、例外とする
            non_pass_actions = [legal_action for legal_action in legal_actions if legal_action != PASS_ACTION]
            if non_pass_actions:
                raise ValueError("Passは選択できません")
        else:
            action_row, action_col = id2position(action)
            if not self._validate_index(action_row, action_col):
                raise ValueError("indexが不正です")
            next_state = self.flip(state, action)
        
        # プレイヤー視点入れ替え(参照を持つビューではなく、独立した配列を生成するためにcopyを使用)
        next_state = next_state[::-1].copy()

        return next_state
      
    def reward(self, done):
        # 報酬の視点 : 各状態のプレイヤー視点
        # 状況	     盤面変化   ゲーム終了  報酬
        # 通常の着手  あり	      しない    0.0
        # パス	     なし	     しない    0.0
        # 勝利	     あり／なし	  する	   +1.0
        # 敗北	     あり／なし	  する	   -1.0
        # 引き分け    あり／なし   する     0.0
        return REWARD_DICT[done]

    def step(self, action, legal_actions):
        state = self.agent_state
        next_state = self.next_state(state, action, legal_actions)
        done = self.is_done(next_state)
        reward = self.reward(done)
        
        self.agent_state = next_state
        
        return next_state, reward, done
    
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
    
    def flip(self, state, action):
        next_state = state.copy()
        # 反転可能な石がない
        flippable_all_positions = self._calc_flippable_positions(state, action)
        if not len(flippable_all_positions):
            return next_state
        
        flippable_rows, flippable_cols = flippable_all_positions[:, 0], flippable_all_positions[:, 1]
        
        # 着手
        action_row, action_col = id2position(action)
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
            return COMPLETE
        
        # 終了条件2: 2人も合法手が存在しない
        current_legal_actions = self.compute_legal_actions(next_state)
        opponent_legal_actions = self.compute_legal_actions(next_state[::-1])
        if current_legal_actions == [PASS_ACTION] and opponent_legal_actions == [PASS_ACTION]:
            return DRAW
        
        # それ以外はゲーム進行中
        return PROGRESS
    
    def _validate_index(self, action_row, action_col):
        if action_row < 0 or action_row >= BOARD_SIZE or action_col < 0 or action_col >= BOARD_SIZE:
            return False
        return True
    
    def _get_blank_actions(self, state):
        occupied      = state.sum(axis=0)
        blank_actions = occupied == BLANK_CELL
        blank_actions = blank_actions.flatten()
        blank_actions = np.where(blank_actions)[0].tolist()
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
        
        for direction_row, direction_col in Othello.DIRECTIONS:
            flippable_positions = []
            next_row = action_row
            next_col = action_col
            
            while True:
                next_row += direction_row
                next_col += direction_col
                
                if not self._validate_index(next_row, next_col):
                    break

                next_cell = state_mask[next_row, next_col].item()

                if not (next_cell == BLANK_CELL or next_cell == STOLEN_CELL or next_cell == OWN_CELL):
                    raise ValueError("不正な値が取得されました")
                    
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
        
        flippable_all_positions = np.array(flippable_all_positions, dtype=BOARD_DTYPE).reshape(-1, 2)
        return flippable_all_positions

class RandomAgent:
    def __init__(self, gamma=0.9):
        
        if (0 > gamma or gamma > 1) or not math.isfinite(gamma):
            raise ValueError("割引率には0~1の値を設定してください。")

        self.memory      = []                                             # (state, action, reward)をappend
        self.gamma       = gamma                                          # 割引率
        self.pi          = defaultdict(dict)                        # 方策(合法手に対してのみ動的に保持する)
        self.V           = defaultdict(float)                         # 状態価値関数
        self.cnts        = defaultdict(int)                         # 各状態ごとのカウント
        
    def get_state_key(self, state):
        if state.dtype != BOARD_DTYPE:
            raise ValueError(f"dtypeが異なります。dtype : {state.dtype}")
        
        if state.shape != (2, BOARD_SIZE, BOARD_SIZE):
            raise ValueError(f"shapeが異なります。shape : {state.shape}")
        
        # stateのメモリ配置がスライスや転置等でずれていた場合は隣り合うように変換する
        return np.ascontiguousarray(state).tobytes()
    
    def remake_pi(self, legal_actions):
        """合法手を考慮した上で方策をランダム化
        """
        if not legal_actions:
            raise ValueError("パスも含めた合法手が存在しません。")

        random_pi        = {}                        # 方策改善後にゴミデータが残り続けないように辞書を初期化
        random_prob      = 1.0 / len(legal_actions)  # 合法手の各行動パターンを取りえる確率
        
        for i in legal_actions:
            random_pi[i] = random_prob
        
        return random_pi

    def get_action(self, state, legal_actions):
        state_key        = self.get_state_key(state)
        if state_key not in self.pi:
            self.pi[state_key] = self.remake_pi(legal_actions)

        pi               = self.pi[state_key]
        actions          = list(pi.keys())
        action_probs     = list(pi.values())
        return np.random.choice(actions, p=action_probs)
    
    def add(self, state, action, reward):
        self.memory.append((state.copy(), action, reward))
    
    def reset(self):
        self.memory.clear()
        
    def eval(self):
        # エピソードの終了から現在の状態までの収益
        G = 0
        for data in reversed(self.memory):
            state, action, reward = data
            state_key = self.get_state_key(state)
            # ステップごとにプレイヤーが入れ替わるから符号はマイナスにする
            G = reward - self.gamma * G
            self.cnts[state_key] += 1
            self.V[state_key] += (G - self.V[state_key]) / self.cnts[state_key]

def main():
    
    env = Othello()
    action = 0
    gamma = 0.9
    state = env.reset()
    agent = RandomAgent(gamma)
    episodes = 100
    
    for episode in range(episodes):
        state = env.reset()
        agent.reset()

        while True:
            legal_actions = env.compute_legal_actions(state)
            action        = agent.get_action(state, legal_actions)
            
            next_state, reward, done = env.step(action, legal_actions)
            agent.add(state, action, reward)

            if done == COMPLETE or done != DRAW:
                agent.eval()
                break
            
            state = next_state

if __name__ == "__main__":
    main()
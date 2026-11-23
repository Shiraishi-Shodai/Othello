import numpy as np
from collections import defaultdict
import math
from common.constants import *
from common.utils import *

class McStateValueAgent:
    def __init__(self, gamma=0.9):

        self.memory      = []                                             # (state, action, reward)をappend
        self.gamma       = gamma                                          # 割引率
        self.pi          = defaultdict(dict)                        # 方策(合法手に対してのみ動的に保持する)
        self.V           = defaultdict(float)                         # 状態価値関数
        self.cnts        = defaultdict(int)                         # 各状態ごとのカウント
    
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
        state_key        = get_state_key(state)
        if state_key not in self.pi:
            self.pi[state_key] = self.remake_pi(legal_actions)

        pi               = self.pi[state_key]
        actions          = list(pi.keys())
        action_probs     = list(pi.values())
        return np.random.choice(actions, p=action_probs).item()
    
    def add(self, state, action, reward, current_player):
        self.memory.append((state.copy(), action, reward, current_player))
    
    def reset(self):
        self.memory.clear()
        
    def eval(self):
        # エピソードの終了から現在の状態までの収益
        G = 0
        for data in reversed(self.memory):
            state, action, reward, _ = data
            state_key = get_state_key(state)
            # ステップごとにプレイヤーが入れ替わるから符号はマイナスにする
            G = reward - self.gamma * G
            self.cnts[state_key] += 1
            self.V[state_key] += (G - self.V[state_key]) / self.cnts[state_key]
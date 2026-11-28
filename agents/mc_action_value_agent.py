import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import math
from collections import defaultdict
from common.utils import *

def greedy_probs(Q, state_key, epsilon, legal_actions):
    # pi : 合法手のみを対象とした方策を動的に生成するため、引数にpiを受け取る
    action_probs = defaultdict(dict)

    # S = state, A = action(合法手)のQ値を取得
    qs = {legal_action : Q[(state_key, legal_action)] for legal_action in legal_actions}

    # epsilon greedy法
    base_probs = epsilon / len(qs)
    action_probs = {action: base_probs for action in qs.keys()}
    max_action = next(a for a, q in qs.items() if q == max(qs.values()))
    action_probs[max_action] += 1.0 - epsilon
    return action_probs
        
class McActionValueAgent:
    def __init__(self, gamma=0.9, alpha=0.9, epsilon=0.1):
        if (0 > gamma or gamma > 1) or not math.isfinite(gamma):
            raise ValueError("割引率には0~1の値を設定してください。")
        
        self.memory = []
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        self.pi    = defaultdict(dict)
        self.Q     = defaultdict(float)
        self.state_cnts  = defaultdict(int)
        self.action_cnts = defaultdict(int)
        
    def remake_pi(self, legal_actions):
        if not legal_actions:
            raise ValueError("パスも含めた合法手が存在しません。")
        
        random_action_probs = defaultdict(dict)
        random_prob = 1.0 / len(legal_actions)

        random_action_probs = {legal_action : random_prob for legal_action in legal_actions}
        
        return random_action_probs
    
    def get_action(self, state, legal_actions):
        state_key = get_state_key(state)
        
        # 方策は動的に生成するため、初めて扱うstateが入力されたときはランダムに方策を初期化する
        if not self.pi[state_key]:
            self.pi[state_key] = self.remake_pi(legal_actions)
        pi = self.pi[state_key]
        actions = list(pi.keys())
        action_probs = list(pi.values())
        
        return np.random.choice(actions, p=action_probs)

    def add(self, state, action, reward, current_player, legal_actions):
        state_key = get_state_key(state)
        # ある状態における訪問回数をカウント
        self.state_cnts[state_key] += 1
        # ある状態におけるある行動を取った際の訪問回数をカウント
        self.action_cnts[(state_key, action)] += 1
        self.memory.append((state, action, reward, current_player, legal_actions))
    
    def reset(self):
        self.memory.clear()
        
    def update(self):
        G = 0
        for data in reversed(self.memory):
            state, action, reward, current_player, legal_actions = data
            state_key = get_state_key(state)
            # 収益 = 割引率付き報酬和
            # 近い将来の報酬ほど重要に見せる(1つのエピソード内の)
            G = reward + self.gamma * G
            action_key = (state_key, action)
            # Agentが置かれる状況(状態遷移確率、方策)はエピソードごとに変化するため、
            # 過去のデータの重要性はエピソードごとに小さくする
            # 近い将来の収益程、重要に見せかける
            # オセロでは、1つのエピソード内に2回以上同じ状態になることはない。(パスの場合であっても、プレイヤーを切り替えるためにstateの0次元目を入れ替えるため状態は変化する)
            # →エピソードを繰り返したとき、後続のエピソードで計算された収益程重要と見せかける
            self.Q[action_key] += (G - self.Q[action_key]) * self.alpha
            self.pi[state_key] = greedy_probs(self.Q, state_key, self.epsilon, legal_actions)

import numpy as np
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from common.constants import *
from common.utils import get_state_key
from common.render import render_q


# ==================================================
# Test 1: 通常の合法手の描画テスト
# ==================================================

def test_normal_actions():

    print("Test 1: 通常の合法手の描画")

    # ----------------------------
    # 1. 初期盤面を作成
    # ----------------------------

    state = np.zeros(
        (2, 8, 8),
        dtype=BOARD_DTYPE
    )

    # BLACKの石
    state[0, 3, 4] = 1  # E4
    state[0, 4, 3] = 1  # D5

    # WHITEの石
    state[1, 3, 3] = 1  # D4
    state[1, 4, 4] = 1  # E5

    current_player = BLACK

    state_key = get_state_key(state)

    # ----------------------------
    # 2. 合法手
    # ----------------------------

    legal_actions = [
        19,  # D3
        26,  # C4
        37,  # F5
        44   # E6
    ]

    # ----------------------------
    # 3. 行動価値
    # ----------------------------

    Q = {
        (state_key, 19): 0.72,
        (state_key, 26): 0.20,
        (state_key, 37): -0.35,
        # E6は未評価
    }

    # ----------------------------
    # 4. 訪問回数
    # ----------------------------

    cnts = {
        (state_key, 19): 50,
        (state_key, 26): 20,
        (state_key, 37): 8,
        # E6は未訪問
    }

    # ----------------------------
    # 5. 描画
    # ----------------------------

    render_q(
        state=state,
        Q=Q,
        cnts=cnts,
        current_player=current_player,
        legal_actions=legal_actions,
        q_limit=1.0
    )


# ==================================================
# Test 2: PASSの描画テスト
# ==================================================

def test_pass_action():

    print("Test 2: PASSの描画")

    # ----------------------------
    # 1. PASSが必要な盤面を作成
    # ----------------------------

    state = np.zeros(
        (2, 8, 8),
        dtype=BOARD_DTYPE
    )

    # 現在のプレイヤー（BLACK）の石
    state[0, 0, 0] = 1

    # 相手プレイヤー（WHITE）の石
    state[1, 0, 2] = 1

    current_player = BLACK

    state_key = get_state_key(state)

    # ----------------------------
    # 2. 合法手
    # ----------------------------

    # BLACKには合法手がないためPASS
    legal_actions = [64]

    # ----------------------------
    # 3. 行動価値
    # ----------------------------

    Q = {
        (state_key, 64): 0.75
    }

    # ----------------------------
    # 4. 訪問回数
    # ----------------------------

    cnts = {
        (state_key, 64): 25
    }

    # ----------------------------
    # 5. 描画
    # ----------------------------

    render_q(
        state=state,
        Q=Q,
        cnts=cnts,
        current_player=current_player,
        legal_actions=legal_actions,
        q_limit=1.0
    )


# ==================================================
# Test 3: PASSが未評価の場合
# ==================================================

def test_pass_unvisited():

    print("Test 3: PASSが未評価の場合")

    state = np.zeros(
        (2, 8, 8),
        dtype=BOARD_DTYPE
    )

    state[0, 0, 0] = 1
    state[1, 0, 2] = 1

    current_player = BLACK

    state_key = get_state_key(state)

    legal_actions = [64]

    # Qとcntsにはまだ登録されていない
    Q = {}
    cnts = {}

    render_q(
        state=state,
        Q=Q,
        cnts=cnts,
        current_player=current_player,
        legal_actions=legal_actions,
        q_limit=1.0
    )


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    test_normal_actions()

    test_pass_action()

    test_pass_unvisited()

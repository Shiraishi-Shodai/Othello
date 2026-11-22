from matplotlib import pyplot as plt
import numpy as np
import japanize_matplotlib
import matplotlib.patches as patches
from common.utils import get_state_key
from common.constants import *

def render_v(state, V, cnts, current_player):
    """
    盤面全体を評価した状態価値 V(s) を、視覚的に表示
    state からオセロ盤面を描画する関数を作る。
    agent.V から状態価値を取得する。
    agent.cnts から訪問回数を取得する。
    盤面の横に状態価値と訪問回数を表示する。
    """
    state_key = get_state_key(state)
    board = state[0] - state[1]
    agent_cells = np.sum(state[0]).item()
    opponent_cells = np.sum(state[1]).item()

    # 盤面の上側に表示する2段分のテキスト
    upper_line1 = f"Agent: {"BLACK" if current_player == BLACK else 'WHITE'}"
    upper_line2 = f"V[state]: {V[state_key]}"
    upper_line3 = f"Agent: {agent_cells}, Opponent: {opponent_cells}"
    upper_line4 = f"訪問回数: {cnts[state_key]}"
    # 縦軸横軸のラベル
    cols = list("abcdefgh")
    rows = [str(i) for i in range(1, 9)]

    fig, ax = plt.subplots(figsize=(6.5, 6.5))

    # 盤面の背景（緑）と外枠（茶色）
    board_bg = patches.Rectangle(
        (0, 0), 8, 8, facecolor="#2E8B46", edgecolor="#5C1616", linewidth=8, zorder=1
    )
    ax.add_patch(board_bg)

    cell_colors = {
        0 : {
            "facecolor" : "#181818",
            "edgecolor" : "#000000",
        },
        1 : {
            "facecolor" : "#EFEFEF",
            "edgecolor" : "#BDBDBD",
        }
    }

    # 8x8 グリッド線（0〜8の整数座標に引く）
    for i in range(9):
        ax.plot([0, 8], [i, i], color="#1B3B24", linewidth=1.2, zorder=2)
        ax.plot([i, i], [0, 8], color="#1B3B24", linewidth=1.2, zorder=2)

    # 石と赤×印を描画（x: 0..7 -> a..h, y: 0..7 -> 1..8）
    for r in range(8):
        for c in range(8):
            cell = board[r, c].item()
            cx, cy = c + 0.5, r + 0.5  # マスの中心座標

            if cell == 1 or cell == -1:
                color_num = current_player if cell == 1 else 1 - current_player
                facecolor = cell_colors[color_num]["facecolor"]
                edgecolor = cell_colors[color_num]["edgecolor"]
                stone = patches.Circle(
                    (cx, cy), radius=0.38, facecolor=facecolor, edgecolor=edgecolor, linewidth=1, zorder=4
                )
                ax.add_patch(stone)
            elif cell == "X":
                ax.text(
                    cx,
                    cy,
                    "×",
                    color="#D62828",
                    fontsize=20,
                    fontweight="bold",
                    ha="center",
                    va="center",
                    zorder=4,
                )

    # 盤面上側（a-h のさらに上）に2段分のテキストを表示
    ax.text(
        4.0,
        -1.25,
        upper_line4,
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="#222222",
        zorder=5,
    )
    ax.text(
        4.0,
        -2.25,
        upper_line3,
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="#333333",
        zorder=5,
    )
    ax.text(
        4.0,
        -3.05,
        upper_line2,
        ha="center",
        va="center",
        fontsize=12,
        color="#444444",
        zorder=5,
    )
    ax.text(
        4.0,
        -4.25,
        upper_line1,
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="#555555",
        zorder=5
    )

    # 軸の設定：横軸 a-h（上）、縦軸 1-8（左・上から下）
    ax.set_xlim(-0.05, 8.05)
    ax.set_ylim(8.05, -0.05)  # y軸を反転して1が上に来るようにする
    ax.set_aspect("equal")

    ax.set_xticks(np.arange(8) + 0.5)
    ax.set_xticklabels(cols, fontsize=14, color="#333333")
    ax.xaxis.tick_top()  # 横軸ラベルを盤面の上に配置
    ax.tick_params(axis="x", length=0, pad=6)

    ax.set_yticks(np.arange(8) + 0.5)
    ax.set_yticklabels(rows, fontsize=14, color="#333333")
    ax.tick_params(axis="y", length=0, pad=8)

    # 外枠のスパインを非表示にしてスッキリさせる
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    plt.show()

# BOARD_SIZE = 8
# OWN_CELL = 1
# BOARD_DTYPE = np.int8
# state = np.zeros((2, BOARD_SIZE, BOARD_SIZE), dtype=BOARD_DTYPE)
# state[0, 3, 4] = OWN_CELL
# state[0, 4, 3] = OWN_CELL
# state[1, 3, 3] = OWN_CELL
# state[1, 4, 4] = OWN_CELL
# current_player = 0

# V = {}
# V[state.tobytes()] = 0.34
# cnts = {}
# cnts[state.tobytes()] = 1

# render_v(state, V, cnts, current_player)
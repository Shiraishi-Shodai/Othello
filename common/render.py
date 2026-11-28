from matplotlib import pyplot as plt
import numpy as np
import japanize_matplotlib
import matplotlib.patches as patches
from common.utils import get_state_key
from common.constants import *
from matplotlib.colors import TwoSlopeNorm
from matplotlib.cm import ScalarMappable
from decimal import Decimal, ROUND_DOWN

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


def render_q(
    state,
    Q,
    action_cnts,
    state_cnts,
    current_player,
    legal_actions,
    q_limit=1.0
):
    """
    行動価値関数 Q(s, a) をオセロ盤面上に描画する。

    Parameters
    ----------
    state : np.ndarray
        現在の盤面状態。
        Shape: (2, 8, 8)
        state[0]: 自分の石
        state[1]: 相手の石

    Q : dict
        Q[(state_key, action)] = 行動価値

    action_cnts : dict
        action_cnts[(state_key, action)] = 行動ごとの訪問回数

    state_cnts : dict
        state_cnts[state_key] = 状態ごとの訪問回数

    current_player : int
        現在のプレイヤー（BLACK または WHITE）

    legal_actions : list[int]
        選択可能な行動。
        0〜63: 盤面の各マス
        64: PASS

    q_limit : float
        ヒートマップの表示範囲。
        初期値は1.0。
    """

    # ----------------------------
    # 1. データの取得
    # ----------------------------

    state = np.asarray(state)

    if state.shape != (2, 8, 8):
        raise ValueError(
            "state の Shape は (2, 8, 8) である必要があります。"
        )

    if q_limit <= 0:
        raise ValueError("q_limit は0より大きい値を指定してください。")

    state_key = get_state_key(state)

    board = state[0] - state[1]

    agent_cells = int(np.sum(state[0]))
    opponent_cells = int(np.sum(state[1]))

    # 現在の状態の訪問回数を取得
    state_visit_count = state_cnts.get(state_key, 0)

    legal_actions = sorted(set(int(a) for a in legal_actions))

    if any(a < 0 or a > 64 for a in legal_actions):
        raise ValueError("action は0〜64の範囲で指定してください。")

    # ----------------------------
    # 2. 共通表示情報
    # ----------------------------

    player_name = "BLACK" if current_player == BLACK else "WHITE"

    header = (
        f"手番: {player_name}  |  "
        f"自石: {agent_cells}  |  "
        f"相手石: {opponent_cells}  |  "
        f"状態訪問回数: {state_visit_count}"
    )

    # ----------------------------
    # 3. ヒートマップの設定
    # ----------------------------

    # 負の値：赤
    # 0付近：黄色
    # 正の値：緑
    cmap = plt.get_cmap("RdYlGn")

    norm = TwoSlopeNorm(
        vmin=-q_limit,
        vcenter=0,
        vmax=q_limit
    )

    # ----------------------------
    # 4. PASSの表示情報
    # ----------------------------

    pass_key = (state_key, 64)

    pass_q = Q.get(pass_key)
    pass_cnt = action_cnts.get(pass_key, 0)

    if 64 in legal_actions:

        if pass_q is None:
            pass_color = "#BDBDBD"
            pass_value_text = "Q値: 未評価"

        else:
            pass_q = float(pass_q)
            pass_color = cmap(norm(pass_q))
            pass_value_text = f"Q値: {pass_q:+.3f}"

        pass_count_text = f"行動訪問回数: {pass_cnt}"

    else:
        pass_color = "#E5E5E5"
        pass_value_text = "非合法"
        pass_count_text = ""

    # ----------------------------
    # 5. 描画領域の作成
    # ----------------------------

    fig = plt.figure(figsize=(10, 7.5))

    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[8, 2.5],
        wspace=0.25
    )

    ax = fig.add_subplot(gs[0, 0])
    pass_ax = fig.add_subplot(gs[0, 1])

    fig.suptitle(
        "Action Value Function Q(s, a)",
        fontsize=16,
        fontweight="bold",
        y=0.97
    )

    fig.text(
        0.42,
        0.92,
        header,
        ha="center",
        fontsize=10,
        color="#333333"
    )

    # ----------------------------
    # 6. 盤面背景
    # ----------------------------

    board_bg = patches.Rectangle(
        (0, 0),
        8,
        8,
        facecolor="#2E8B46",
        edgecolor="#5C1616",
        linewidth=8,
        zorder=1
    )

    ax.add_patch(board_bg)

    # ----------------------------
    # 7. 合法手の行動価値を描画
    # ----------------------------

    for action in legal_actions:

        # PASSは盤面上に描画しない
        if action == 64:
            continue

        # 行動IDから盤面座標を取得
        row, col = divmod(action, 8)

        # Q値と行動訪問回数を取得
        action_key = (state_key, action)

        q_value = Q.get(action_key)
        action_visit_count = action_cnts.get(action_key, 0)

        # 行動価値が未評価の場合
        if q_value is None:

            facecolor = "#BDBDBD"
            label = f"未評価\nn={action_visit_count}"

        else:

            q_value = float(q_value)

            facecolor = cmap(norm(q_value))
            label = f"{q_value:+.5f}\nn={action_visit_count}"

        # 行動価値に応じてマスを着色
        action_cell = patches.Rectangle(
            (col + 0.06, row + 0.06),
            0.88,
            0.88,
            facecolor=facecolor,
            edgecolor="#222222",
            linewidth=0.8,
            alpha=0.8,
            zorder=2
        )

        ax.add_patch(action_cell)

        # Q値と行動訪問回数を表示
        ax.text(
            col + 0.5,
            row + 0.5,
            label,
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="#111111",
            bbox={
                "facecolor": "white",
                "alpha": 0.78,
                "edgecolor": "none",
                "boxstyle": "round,pad=0.15"
            },
            zorder=5
        )

    # ----------------------------
    # 8. 盤面のグリッド線
    # ----------------------------

    for i in range(9):

        ax.plot(
            [0, 8],
            [i, i],
            color="#1B3B24",
            linewidth=1.2,
            zorder=3
        )

        ax.plot(
            [i, i],
            [0, 8],
            color="#1B3B24",
            linewidth=1.2,
            zorder=3
        )

    # ----------------------------
    # 9. 石の描画
    # ----------------------------

    cell_colors = {
        BLACK: {
            "facecolor": "#181818",
            "edgecolor": "#000000"
        },
        WHITE: {
            "facecolor": "#EFEFEF",
            "edgecolor": "#BDBDBD"
        }
    }

    for row in range(8):
        for col in range(8):

            cell = board[row, col].item()

            if cell == 1 or cell == -1:

                # 自分の石か相手の石かを判定
                color_num = (
                    current_player if cell == 1
                    else 1 - current_player
                )

                stone = patches.Circle(
                    (col + 0.5, row + 0.5),
                    radius=0.38,
                    facecolor=cell_colors[color_num]["facecolor"],
                    edgecolor=cell_colors[color_num]["edgecolor"],
                    linewidth=1,
                    zorder=4
                )

                ax.add_patch(stone)

    # ----------------------------
    # 10. カラーバー
    # ----------------------------

    mappable = ScalarMappable(
        norm=norm,
        cmap=cmap
    )

    mappable.set_array([])

    colorbar = fig.colorbar(
        mappable,
        ax=ax,
        fraction=0.046,
        pad=0.04
    )

    colorbar.set_label(
        "Action Value Q(s, a)",
        fontsize=11
    )

    colorbar.set_ticks([-q_limit, 0, q_limit])

    # ----------------------------
    # 11. PASS専用表示領域
    # ----------------------------

    pass_ax.set_xlim(0, 1)
    pass_ax.set_ylim(0, 1)

    pass_ax.set_title(
        "PASS の行動価値",
        fontsize=12,
        fontweight="bold",
        pad=15
    )

    # PASSの背景
    pass_panel = patches.FancyBboxPatch(
        (0.08, 0.30),
        0.84,
        0.48,
        boxstyle="round,pad=0.03",
        facecolor=pass_color,
        edgecolor="#555555",
        linewidth=1.5,
        alpha=0.9
    )

    pass_ax.add_patch(pass_panel)

    # PASSラベル
    pass_ax.text(
        0.5,
        0.67,
        "PASS",
        ha="center",
        va="center",
        fontsize=16,
        fontweight="bold",
        color="#222222"
    )

    # PASSのQ値
    pass_ax.text(
        0.5,
        0.52,
        pass_value_text,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color="#222222"
    )

    # PASSの行動訪問回数
    pass_ax.text(
        0.5,
        0.40,
        pass_count_text,
        ha="center",
        va="center",
        fontsize=10,
        color="#333333"
    )

    pass_ax.text(
        0.5,
        0.17,
        "盤面上のマスとは\n別に表示",
        ha="center",
        va="center",
        fontsize=9,
        color="#555555"
    )

    pass_ax.axis("off")

    # ----------------------------
    # 12. 盤面の軸設定
    # ----------------------------

    cols = list("abcdefgh")
    rows = [str(i) for i in range(1, 9)]

    ax.set_xlim(-0.05, 8.05)
    ax.set_ylim(8.05, -0.05)
    ax.set_aspect("equal")

    ax.set_xticks(np.arange(8) + 0.5)
    ax.set_xticklabels(
        cols,
        fontsize=14,
        color="#333333"
    )

    ax.xaxis.tick_top()
    ax.tick_params(axis="x", length=0, pad=6)

    ax.set_yticks(np.arange(8) + 0.5)
    ax.set_yticklabels(
        rows,
        fontsize=14,
        color="#333333"
    )

    ax.tick_params(axis="y", length=0, pad=8)

    # 外枠を非表示
    for spine in ax.spines.values():
        spine.set_visible(False)

    # ----------------------------
    # 13. 表示
    # ----------------------------

    fig.text(
        0.42,
        0.035,
        "各マス: Q値 / 行動訪問回数 n",
        ha="center",
        fontsize=10,
        color="#444444"
    )

    fig.subplots_adjust(
        top=0.85,
        bottom=0.09,
        left=0.08,
        right=0.93
    )

    plt.show()

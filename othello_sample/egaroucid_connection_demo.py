import subprocess
from pathlib import Path

def send_gtp(engine, command: str) -> str:
    """GTPコマンドを送り、空行まで応答を読み取る。"""
    assert engine.stdin is not None
    assert engine.stdout is not None

    engine.stdin.write(command + "\n")
    engine.stdin.flush()

    response = []

    while True:
        line = engine.stdout.readline()

        if line == "":
            raise RuntimeError("Egaroucidが応答前に終了しました")

        if line.strip() == "":
            break

        response.append(line.rstrip("\r\n"))

    return "\n".join(response)


egaroucid_path = r"C:/Users/siran/ML-Projects/Egaroucid_for_Console_7_8_1_Windows_SIMD/Egaroucid_for_Console_7_8_1_SIMD.exe"
exe = Path(egaroucid_path)

engine = subprocess.Popen(
    [str(exe), "-gtp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    cwd=exe.parent,
    bufsize=1,
)

# engine.stdin にコマンドを送り、
# engine.stdout から応答を読み取る

try:
    print(send_gtp(engine, "protocol_version"))
    print(send_gtp(engine, "name"))
    print(send_gtp(engine, "version"))
    # print(send_gtp(engine, "list_commands"))
    
    # 利用できるコマンドの確認
    # commands = [
    # "clear_board",
    # "gogui-rules_game_id",
    # "showboard",
    # "gogui-rules_legal_moves",
    # "gogui-rules_side_to_move",
    # ]
    
    # for command in commands:
    #     print(f"\n>>> {command}")
    #     print(send_gtp(engine, command))
    
    # AIに手を打たせる
    print(send_gtp(engine, "showboard"))
    # print(send_gtp(engine, "genmove black"))
    # print(send_gtp(engine, "showboard"))
    print(">>> genmove black")
    print(send_gtp(engine, "genmove black"))

    print("\n>>> showboard")
    print(send_gtp(engine, "showboard"))

    print("\n>>> gogui-rules_side_to_move")
    print(send_gtp(engine, "gogui-rules_side_to_move"))
    
finally:
    if engine.poll() is None:
        engine.stdin.write("quit\n")
        engine.stdin.flush()
        engine.wait(timeout=5)
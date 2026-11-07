import torch

def encode_state(board: torch.Tensor, turn: int) -> torch.Tensor:
    """
    黒の手番：
    - Channel 0 = 黒石
    - Channel 1 = 白石
    白の手番：
    - Channel 0 = 白石
    - Channel 1 = 黒石

    board: 0=空き、1=黒、2=白
    turn: 1=黒、2=白
    
    チャンネル	意味	値
    Channel 0	自分の石	0 or 1
    Channel 1	相手の石	0 or 1
    Returns:  (2, 8, 8)
    """
    channel1 = board
    
    return channel1
    
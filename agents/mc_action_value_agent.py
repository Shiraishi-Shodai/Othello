import math

class McActionValueAgent:
    def __init__(self, gamma, alpha):
        if (0 > gamma or gamma > 1) or not math.isfinite(gamma):
            raise ValueError("割引率には0~1の値を設定してください。")
        
        self.memory = []
        self.alpha = alpha
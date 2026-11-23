import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), r"../../../"))
for i in sys.path:
    print(i)
from common.constants import *
from common.utils import *
from common.render import render_v
from tqdm import tqdm
from envs.othello import Othello
from agents.mc_state_value_agent import McStateValueAgent

def main():
    
    env = Othello()
    action = 0
    gamma = 0.9
    state = env.reset()
    agent = McStateValueAgent(gamma)
    episodes = 100
    
    valid_gamma(gamma)
    
    for episode in tqdm(range(episodes),
                        desc="Gaming now!",
                        unit="episode"):
        state = env.reset()
        agent.reset()

        while True:
            legal_actions = env.compute_legal_actions(state)
            action        = agent.get_action(state, legal_actions)
            
            next_state, reward, done, current_player = env.step(action, legal_actions)
            agent.add(state, action, reward, current_player)

            if done:
                agent.eval()
                break
            
            state = next_state

    for i in agent.memory:
        state, action, reward, current_player = i
        render_v(state, agent.V, agent.cnts, current_player)
        
if __name__ == "__main__":
    main()

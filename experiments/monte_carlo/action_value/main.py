import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
from envs.othello import Othello
from agents.mc_action_value_agent import McActionValueAgent
from common.render import *
from tqdm import tqdm

def main():
    gamma = 0.9
    alpha = 0.1
    epsilon = 0.1
    episodes = 100

    env = Othello()
    agent = McActionValueAgent(
        gamma=gamma,
        alpha=alpha,
        epsilon=epsilon
    )
    
    for episode in tqdm(
                    range(episodes),
                    desc=f"Game playing! episodes: {episodes}"):
        state = env.reset()
        agent.reset()
        
        while True:
            legal_actions = env.compute_legal_actions(state)
            action = agent.get_action(state, legal_actions)
            next_state, reward, done, current_player = env.step(action, legal_actions)
            agent.add(state, action, reward, current_player, legal_actions)

            if done:
                agent.update()
                break
            
            state = next_state
    
    for data in agent.memory:
        state, action, reward, current_player, legal_actions = data
        render_q(
            state=state,
            Q=agent.Q,
            action_cnts=agent.action_cnts,
            state_cnts=agent.state_cnts,
            current_player=current_player,
            legal_actions=legal_actions,
            q_limit=1.0
        )

if __name__ == "__main__":
    main()
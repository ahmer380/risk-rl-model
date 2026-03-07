from src.train.ppo import RiskPPO
from src.train.rl_agent import RLAgent

def train(map_name: str, num_players: int):
    ppo_trainer = RiskPPO(map_name, num_players)
    ppo_trainer.train(total_timesteps=5000)
    ppo_trainer.save("v1")

def load_rl_agent(player_id: int, map_name: str, num_players: int) -> RLAgent:
    ppo_trainer = RiskPPO(map_name, num_players)
    ppo_trainer.load("v1")

    return RLAgent(player_id=player_id, risk_ppo=ppo_trainer)

if __name__ == "__main__":
    train("mini", 2)

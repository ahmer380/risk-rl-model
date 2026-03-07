from src.environment.map import RiskMap

from src.train.gym_runner import GymRunner
from src.train.ppo import RiskPPO
from src.train.rl_agent import RLAgent

def train(map_name: str, num_players: int):
    risk_map = RiskMap.from_json(f"maps/{map_name}.json")
    gym_runner = GymRunner(risk_map, num_players)
    ppo_trainer = RiskPPO(gym_runner)
    ppo_trainer.train(total_timesteps=5000)
    ppo_trainer.save(f"ppo_{map_name}_map_{num_players}_player_agent")

def load_rl_agent(player_id: int, map_name: str, num_players: int) -> RLAgent:
    risk_map = RiskMap.from_json(f"maps/{map_name}.json")
    gym_runner = GymRunner(risk_map, num_players)
    ppo_trainer = RiskPPO(gym_runner)
    ppo_trainer.load(f"ppo_{map_name}_map_{num_players}_player_agent")

    return RLAgent(player_id=player_id, risk_ppo=ppo_trainer)

if __name__ == "__main__":
    train("mini", 2)

import argparse

from src.train.ppo import RiskPPO
from src.train.rl_agent import RLAgent

def train(map_name: str, num_players: int):
    ppo_trainer = RiskPPO(map_name, num_players)
    ppo_trainer.train()
    ppo_trainer.save("v1")

def load_rl_agent(map_name: str, num_players: int) -> RLAgent:
    ppo_trainer = RiskPPO(map_name, num_players)
    ppo_trainer.load("v1")

    return RLAgent(ppo_trainer)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a PPO agent for the Risk environment.")
    parser.add_argument(
        "--map_name",
        default="mini",
        help="Map name to train on (e.g. mini, classic). Defaults to mini.",
    )
    parser.add_argument(
        "--num_players",
        type=int,
        default=2,
        help="Number of players in the environment. Defaults to 2.",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    train(args.map_name, args.num_players)

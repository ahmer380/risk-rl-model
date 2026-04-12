import argparse

from src.environment.map import RiskMap

from src.train.ppo import RiskPPO

from src.utils.k_clique_generator import KCliqueGenerator

def train(map_name: str, num_players: int, clique_size: int, clique_density: str):
    if map_name.startswith("clique"):
        density = 2/clique_size if clique_density.lower() == "min" else 1.0
        risk_map = RiskMap.from_json(json_data=KCliqueGenerator.generate(k=clique_size, density=density))
    else:
        risk_map = RiskMap.from_json(f"maps/{map_name}.json")

    ppo_trainer = RiskPPO(
        risk_map=risk_map,
        num_players=num_players,
    )
    ppo_trainer.train(total_timesteps=3_000)
    ppo_trainer.save()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a PPO agent for the Risk environment.")
    parser.add_argument(
        "--map_name",
        type=str,
        default="mini",
        help="Map name to train on (e.g. mini, classic, clique). Defaults to mini.",
    )
    parser.add_argument(
        "--num_players",
        type=int,
        default=2,
        help="Number of players in the environment. Defaults to 2.",
    )
    parser.add_argument(
        "--clique_size",
        type=int,
        help="Size of the clique to generate if map_name starts with 'clique'.",
    )
    parser.add_argument(
        "--clique_density",
        type=str,
        help="Density of the clique to generate if map_name starts with 'clique'. Must be either max or min to ensure deterministic generation.",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    train(args.map_name, args.num_players, args.clique_size, args.clique_density)

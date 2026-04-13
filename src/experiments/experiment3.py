from src.agents.agent import Agent, RandomAgent, CommunistAgent, CapitalistAgent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

from src.train.rl_agent import RLAgent

from src.utils.k_clique_generator import KCliqueGenerator

if __name__ == "__main__":
    Agent.reset_player_ids()
    risk_map = RiskMap.from_json(json_data=KCliqueGenerator.generate(k=8, density=1.0))
    agents = [RLAgent(risk_map, 2, "v1"), RandomAgent()]
    simulation_runner = SimulationRunner("RLAgent vs Communist static player ordering", risk_map, agents, 1000, observers=[OutcomeObserver(), BattleObserver()], shuffle_turn_order=True)
    simulation_runner.run_simulation()
    # simulation_runner.summarise_game()
    simulation_runner.summarise_simulation()

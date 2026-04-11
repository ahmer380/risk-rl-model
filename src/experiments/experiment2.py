from src.agents.agent import Agent, RandomAgent, CommunistAgent, CapitalistAgent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

from src.train.rl_agent import RLAgent

if __name__ == "__main__":
    Agent.reset_player_ids()
    risk_map = RiskMap.from_json(path="maps/mini.json")
    agents = [RLAgent(risk_map, 2, 1), CommunistAgent(disparity=0)]
    simulation_runner = SimulationRunner("RLAgent vs Communist static player ordering", risk_map, agents, 100, observers=[OutcomeObserver(), BattleObserver()], shuffle_turn_order=False)
    simulation_runner.run_simulation()
    simulation_runner.summarise_simulation()

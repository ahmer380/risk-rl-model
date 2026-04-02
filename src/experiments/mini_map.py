from src.agents.agent import Agent, RandomAgent, CommunistAgent, CapitalistAgent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

if __name__ == "__main__":
    Agent.reset_player_ids()
    risk_map = RiskMap.from_json(path="maps/mini.json")
    agents = [CommunistAgent(disparity=0), CommunistAgent(disparity=0)]
    simulation_runner = SimulationRunner("Communist vs Communist static player ordering", risk_map, agents, 1000, observers=[OutcomeObserver(), BattleObserver()], shuffle_turn_order=False)
    simulation_runner.run_simulation()
    simulation_runner.summarise_simulation()

if __name__ == "__main__":
    Agent.reset_player_ids()
    risk_map = RiskMap.from_json(path="maps/mini.json")
    agents = [CommunistAgent(disparity=0), CommunistAgent(disparity=0)]
    simulation_runner = SimulationRunner("Communist vs Communist shuffled player ordering", risk_map, agents, 1000, observers=[OutcomeObserver(), BattleObserver()], shuffle_turn_order=True)
    simulation_runner.run_simulation()
    simulation_runner.summarise_simulation()

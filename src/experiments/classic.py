from src.agents.agent import Agent, RandomAgent, CommunistAgent, CapitalistAgent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

if __name__ == "__main__":
    Agent.reset_player_ids()
    risk_map = RiskMap.from_json("maps/classic.json")
    agents = [CapitalistAgent(capitals=3, disparity=10), CommunistAgent()]
    simulation_runner = SimulationRunner("Classic Map Simulation 1", risk_map, agents, 100, observers=[OutcomeObserver(), BattleObserver()])
    simulation_runner.run_simulation()
    simulation_runner.summarise_simulation()

if __name__ == "__main__":
    Agent.reset_player_ids()
    risk_map = RiskMap.from_json(path="maps/classic.json")
    agents = [CommunistAgent(), RandomAgent(), RandomAgent(), CapitalistAgent(disparity=3)]
    simulation_runner = SimulationRunner("Classic Map Simulation 2", risk_map, agents, 100, observers=[OutcomeObserver(), BattleObserver()], shuffle_turn_order=True)
    simulation_runner.run_simulation()
    simulation_runner.summarise_simulation()

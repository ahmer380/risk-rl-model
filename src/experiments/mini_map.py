from src.agents.agent import RandomAgent, CommunistAgent, CapitalistAgent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

if __name__ == "__main__":
    risk_map = RiskMap.from_json("maps/mini.json")
    agents = [CommunistAgent(0, disparity=2), CapitalistAgent(1, disparity=5, capitals=1)]
    simulation_runner = SimulationRunner(risk_map, agents, 100, observers=[OutcomeObserver(), BattleObserver()])
    simulation_runner.run_simulation()
    simulation_runner.summarise_simulation()

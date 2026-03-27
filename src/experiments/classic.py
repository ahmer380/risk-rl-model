from src.agents.agent import RandomAgent, CommunistAgent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

if __name__ == "__main__":
    risk_map = RiskMap.from_json("maps/classic.json")
    agents = [CommunistAgent(0), RandomAgent(1)]
    simulation_runner = SimulationRunner(risk_map, agents, 100, observers=[OutcomeObserver(), BattleObserver()])
    simulation_runner.run_simulation()
    # simulation_runner.summarise_game()
    simulation_runner.summarise_simulation()

# if __name__ == "__main__":
#     risk_map = RiskMap.from_json("maps/classic.json")
#     agents = [CommunistAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3), RandomAgent(4), CommunistAgent(5)]
#     simulation_runner = SimulationRunner(risk_map, agents, 100, observers=[OutcomeObserver(), BattleObserver()])
#     simulation_runner.run_simulation()
#     # simulation_runner.summarise_game()
#     simulation_runner.summarise_simulation()

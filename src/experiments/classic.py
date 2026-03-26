from src.agents.agent import RandomAgent, AdvantageAttackAgent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

if __name__ == "__main__":
    risk_map = RiskMap.from_json("maps/classic.json")
    agents = [AdvantageAttackAgent(0), RandomAgent(1)]
    simulation_runner = SimulationRunner(risk_map, agents, 100, observers=[OutcomeObserver(), BattleObserver()])
    simulation_runner.run_simulation()
    # simulation_runner.summarise_game()
    simulation_runner.summarise_simulation()
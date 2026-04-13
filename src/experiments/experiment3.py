from src.agents.agent import Agent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

from src.train.rl_agent import RLAgent

from src.utils.k_clique_generator import KCliqueGenerator

if __name__ == "__main__":
    Agent.reset_player_ids()
    risk_map = RiskMap.from_json(json_data=KCliqueGenerator.generate(k=8, density=0.25))
    simulation_runner = SimulationRunner(
        title="RLAgent Test",
        risk_map=risk_map,
        agents=[RLAgent(risk_map, 2)],
        num_episodes=1000,
        observers=[OutcomeObserver(), BattleObserver()],
        enable_rl_agent_performance_test=True,
        rl_agent_performance_test_num_players=2
    )
    simulation_runner.run_simulation()
    simulation_runner.summarise_simulation()

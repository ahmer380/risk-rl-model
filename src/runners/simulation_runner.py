from src.agents.agent import Agent, RandomAgent, AdvantageAttackAgent

from src.environment.map import RiskMap

from src.observers.observer_manager import ObserverManager

from src.runners.game_runner import GameRunner

class SimulationRunner:
    """Manages the execution of multiple Risk game episodes, for RL training and aggregate experimental analysis."""
    def __init__(
        self,
        risk_map: RiskMap,
        agents: list[Agent],
        num_episodes: int,
        enable_outcome_observer = False,
        enable_battle_observer = False,
        enable_temporal_observer = False,
        max_episode_length = 1000000,
    ):
        self.risk_map = risk_map
        self.agents = agents
        self.num_episodes = num_episodes
        self.max_episode_length = max_episode_length
        self.enable_outcome_observer = enable_outcome_observer
        self.enable_battle_observer = enable_battle_observer
        self.enable_temporal_observer = enable_temporal_observer
        
        self.game_observations: list[ObserverManager] = []
    
    def run_simulation(self):
        for episode in range(self.num_episodes):
            print(f"Starting episode {episode + 1}")
            observer_manager = ObserverManager(self.risk_map, len(self.agents), self.enable_outcome_observer, self.enable_battle_observer, self.enable_temporal_observer)
            self.game_observations.append(observer_manager)
            game_runner = GameRunner(self.risk_map, self.agents, observer_manager, self.max_episode_length)
            game_runner.run_episode()
    
    def summarise_observations(self):
        for i, observer_manager in enumerate(self.game_observations):
            print(f"\n**** Summarising observations for episode {i + 1} ****")
            observer_manager.summarise()

if __name__ == "__main__":
    risk_map = RiskMap.from_json("maps/classic.json")
    agents = [AdvantageAttackAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3)]
    simulation_runner = SimulationRunner(risk_map, agents, 10, True, False, False)
    simulation_runner.run_simulation()
    simulation_runner.summarise_observations()
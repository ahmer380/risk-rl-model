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
        enable_action_count_observer = False,
        max_episode_length = 1000000,
    ):
        self.risk_map = risk_map
        self.agents = agents
        self.num_episodes = num_episodes
        self.max_episode_length = max_episode_length
        self.enable_outcome_observer = enable_outcome_observer
        self.enable_battle_observer = enable_battle_observer
        self.enable_action_count_observer = enable_action_count_observer
        
        self.game_observations: list[ObserverManager] = []
    
    def run_simulation(self):
        for episode in range(self.num_episodes):
            print(f"\rStarting episode {episode + 1}/{self.num_episodes}", end="")
            observer_manager = ObserverManager(self.risk_map, len(self.agents), self.enable_outcome_observer, self.enable_battle_observer, self.enable_action_count_observer)
            self.game_observations.append(observer_manager)
            game_runner = GameRunner(self.risk_map, self.agents, observer_manager, self.max_episode_length)
            game_runner.run_episode()
    
    def summarise_game(self, episode: int = None):
        if not self.game_observations[0].observers:
            return
        
        if episode is not None:
            print(f"\n**** Summarising observations for episode {episode} ****")
            self.game_observations[episode - 1].summarise_game()
        else: # Summarise all episodes
            for i, observer_manager in enumerate(self.game_observations):
                print(f"\n**** Summarising observations for episode {i + 1} ****")
                observer_manager.summarise_game()

    def summarise_simulation(self):
        for i, observer in enumerate(self.game_observations[0].observers):
            observers = [observer_manager.observers[i] for observer_manager in self.game_observations]
            print(observer.summarise_simulation(observers))

if __name__ == "__main__":
    risk_map = RiskMap.from_json("maps/classic.json")
    agents = [AdvantageAttackAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3)]
    simulation_runner = SimulationRunner(risk_map, agents, 10, True, True, False)
    simulation_runner.run_simulation()
    # simulation_runner.summarise_game()
    simulation_runner.summarise_simulation()
from src.agents.agent import Agent, RandomAgent, AdvantageAttackAgent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.observer import Observer
from src.observers.observer_manager import ObserverManager
from src.observers.outcome_observer import OutcomeObserver

from src.runners.game_runner import GameRunner

class SimulationRunner:
    """Manages the execution of multiple Risk game episodes, for RL training and aggregate experimental analysis."""
    def __init__(
        self,
        risk_map: RiskMap,
        agents: list[Agent],
        num_episodes: int,
        observers: list[Observer] = [],
        max_episode_length = 100000,
    ):
        self.risk_map = risk_map
        self.agents = agents
        self.num_episodes = num_episodes
        self.max_episode_length = max_episode_length
        self.observers = observers
        
        self.game_observations: list[ObserverManager] = []
    
    def run_simulation(self):
        for episode in range(self.num_episodes):
            print(f"\rStarting episode {episode + 1}/{self.num_episodes}", end="")
            observers = [observer.clean_copy() for observer in self.observers]
            observer_manager = ObserverManager(
                self.risk_map, 
                len(self.agents),
                observers,
            )
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
        
        if self.game_observations[0].observers:
            truncated_episodes = [observer_manager for observer_manager in self.game_observations if observer_manager.observers[0].action_count == self.max_episode_length]
            print(f"\n{len(truncated_episodes)}/{self.num_episodes} episodes reached the maximum episode length of {self.max_episode_length} and were truncated.")

if __name__ == "__main__":
    risk_map = RiskMap.from_json("maps/classic.json")
    agents = [AdvantageAttackAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3), RandomAgent(4), AdvantageAttackAgent(5)]
    simulation_runner = SimulationRunner(risk_map, agents, 100, observers=[OutcomeObserver(), BattleObserver()])
    simulation_runner.run_simulation()
    # simulation_runner.summarise_game()
    simulation_runner.summarise_simulation()
from src.agents.agent import Agent, RandomAgent, AdvantageAttackAgent

from src.environment.map import RiskMap

from src.observers.observer_manager import ObserverManager
from src.observers.trajectory_observer import TrajectoryObserver

from src.runners.game_runner import GameRunner

class RLTrainer:
    def __init__(self, risk_map: RiskMap, agents: list[Agent]):
        self.risk_map = risk_map
        self.agents = agents
        self.training_iterations: int = 10
        self.max_episode_length: int = 100000

    def train(self):
        for episode in range(self.training_iterations):
            print(f"\rTraining for episode {episode + 1}/{self.training_iterations}", end="")
            trajectory_observer = TrajectoryObserver()
            game_runner = GameRunner(
                self.risk_map,
                self.agents,
                ObserverManager(self.risk_map, len(self.agents), observers=[trajectory_observer]),
                self.max_episode_length
            )
            game_runner.run_episode()
            # print(trajectory_observer.summarise_game())

if __name__ == "__main__":
    agents = [AdvantageAttackAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3), RandomAgent(4), AdvantageAttackAgent(5)]
    risk_map = RiskMap.from_json("maps/classic.json")
    trainer = RLTrainer(risk_map, agents)
    trainer.train()
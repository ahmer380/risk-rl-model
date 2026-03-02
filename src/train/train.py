from src.agents.agent import Agent, RandomAgent, AdvantageAttackAgent

from src.environment.map import RiskMap

from src.observers.observer_manager import ObserverManager

from src.runners.game_runner import GameRunner

class RLTrainer:
    def __init__(self, risk_map: RiskMap, agents: list[Agent]):
        self.risk_map = risk_map
        self.agents = agents
        self.training_episode_iteration: int = 100
        self.max_episode_length: int = 100000

    def train(self):
        for episode in range(self.training_episode_iteration):
            print(f"\rStarting episode {episode + 1}/{self.training_episode_iteration}", end="")
            observer_manager = ObserverManager(
                self.risk_map, 
                len(self.agents),
                enable_trajectory_observer=True # TODO: Extract trajectory observer object after observerManager refactor
            )
            game_runner = GameRunner(self.risk_map, self.agents, observer_manager, self.max_episode_length)
            game_runner.run_episode() 

if __name__ == "__main__":
    agents = [AdvantageAttackAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3), RandomAgent(4), AdvantageAttackAgent(5)]
    risk_map = RiskMap.from_json("maps/classic.json")
    trainer = RLTrainer(risk_map, agents)
    trainer.train()
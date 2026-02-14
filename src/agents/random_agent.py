import random

from src.agents.agent import Agent

from src.environment.actions import Action
from src.environment.game_state import GameState

class RandomAgent(Agent):
    def select_action(self, valid_actions: list[Action], _: GameState) -> Action:
        return random.choice(valid_actions)
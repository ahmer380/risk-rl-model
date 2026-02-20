from abc import ABC

from src.agents.strategy import Strategy

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState

class FortifyStrategy(Strategy, ABC):
    pass

class RandomFortifyStrategy(FortifyStrategy):
    def select_action(self, valid_actions: ActionList, _: GameState) -> Action:
        return valid_actions.get_random_action()
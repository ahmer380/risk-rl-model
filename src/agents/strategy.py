from abc import ABC, abstractmethod

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState

class Strategy(ABC):
    @abstractmethod
    def select_action(self, valid_actions: ActionList, game_state: GameState) -> Action:
        """Select an action from the list of valid actions based on the current game state and the strategy's policy."""
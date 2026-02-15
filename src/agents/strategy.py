from abc import ABC, abstractmethod

from src.environment.actions import Action
from src.environment.game_state import GameState

class Strategy(ABC):
    @abstractmethod
    def select_action(self, valid_actions: list[Action], game_state: GameState) -> Action:
        """Select an action from the list of valid actions based on the current game state and the strategy's policy."""
    
    @abstractmethod
    def segment_action_list(self, valid_actions: list[Action]) -> tuple[list[Action]]:
        """Segment a list of valid actions into sublists based on their type"""
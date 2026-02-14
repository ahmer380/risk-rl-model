from abc import ABC, abstractmethod

from src.environment.actions import Action
from src.environment.game_state import GameState

class Agent(ABC):
    def __init__(self, player_id: int):
        self.player_id = player_id

    @abstractmethod
    def select_action(self, valid_actions: list[Action], game_state: GameState) -> Action:
        """Select an action from the list of valid actions based on the current game state and the agent's policy."""
    
    def reset(self):
        """Reset any internal state of the agent if necessary for the start of a new episode."""
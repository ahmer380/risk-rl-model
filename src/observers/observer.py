from abc import ABC

from src.environment.actions import Action
from src.environment.game_state import GameState
from src.environment.map import RiskMap

from src.observers.player_data import PlayerData

class Observer(ABC):
    """Abstract base class for observers to track specific elements of a single Risk game.
    Observers are NOT responsible for influencing the environment state nor agent decisions/rewards."""
    def __init__(self, risk_map: RiskMap, player_datum: list[PlayerData]):
        self.risk_map = risk_map
        self.player_datum = player_datum

    def on_game_start(self):
        """Called at the start of a game episode."""
    
    def on_action_list_generated(self, action_list: list[Action]):
        """Called after the environment generates the list of valid actions for the current state"""

    def on_action_taken(self, action: Action, previous_state: GameState, current_state: GameState):
        """Called after an action is taken, such that current_state = action.apply(previous_state)."""

    def on_game_end(self, terminal_state: GameState):
        """Called at the end of a game episode, with the final terminal state."""
    
    def summarise(self) -> str:
        """Generate a human-readable summary of the observed game episode based on the collected data for the particular observer."""
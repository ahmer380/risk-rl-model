from typing import Self

from abc import ABC

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap

from src.observers.player_telemetry import PlayerTelemetry

class Observer(ABC):
    """Abstract base class for observers to track specific elements of a single Risk game.
    Observers are NOT responsible for influencing the environment state nor agent decisions/rewards."""
    def __init__(self, core_observer: "CoreObserver"):
        self.core_observer = core_observer

    def on_game_start(self):
        """Called at the start of a game episode."""
    
    def on_action_list_generated(self, action_list: ActionList):
        """Called after the environment generates a list of valid actions"""

    def on_action_taken(self, action: Action, previous_state: GameState, current_state: GameState):
        """Called after an action is taken, such that current_state = action.apply(previous_state)."""

    def on_game_end(self, terminal_state: GameState):
        """Called at the end of a game episode, with the final terminal state."""
    
    def summarise_game(self) -> str:
        """Generate a human-readable summary of the observed game episode based on the collected data for the particular observer."""
        return ""
    
    @classmethod
    def summarise_simulation(cls, observers: list[Self]) -> str:
        """Generate a human-readable summary of the observed simulation based on the collected aggregate data for the particular observer"""
        return ""

class CoreObserver(Observer):
    def __init__(self, risk_map: RiskMap, player_telemetries: list[PlayerTelemetry]):
        super().__init__(None)

        self.risk_map = risk_map
        self.player_telemetries = player_telemetries
        self.action_count = 0
        self.turn_count = 1
    
    def on_action_taken(self, _: Action, previous_state: GameState, current_state: GameState):
        for player_telemetry in self.player_telemetries:
            if previous_state.active_players[player_telemetry.player_id] and not current_state.active_players[player_telemetry.player_id]:
                player_telemetry.eliminated_turn_count = self.turn_count

        if previous_state.current_phase == GamePhase.FORTIFY and current_state.current_phase == GamePhase.DRAFT:
            self.turn_count += 1
        
        self.action_count += 1

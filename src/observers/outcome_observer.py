import time

from src.environment.actions import Action
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap

from src.observers.observer import Observer
from src.observers.player_telemetry import PlayerTelemetry

class OutcomeObserver(Observer):
    """Observer for tracking the outcome of the game, including the winner and final game state."""
    def __init__(self, risk_map: RiskMap, player_telemetries: list[PlayerTelemetry]):
        super().__init__(risk_map, player_telemetries)

        self.terminal_state: GameState = None
        self.running_time: float = None
        self.action_count: int = 0
        self.turn_count: int = 1
    
    def on_game_start(self):
        self.running_time = time.time()
    
    def on_action_taken(self, _: Action, previous_state: GameState, current_state: GameState):
        self.action_count += 1

        if previous_state.current_phase == GamePhase.FORTIFY and current_state.current_phase == GamePhase.DRAFT:
            self.turn_count += 1
        
    def on_game_end(self, terminal_state: GameState):
        self.running_time = time.time() - self.running_time
        self.terminal_state = terminal_state
    
    def summarise(self) -> str:
        lines = ["#### Outcome Observations ####"]
        lines.append(f"Episode ended after {self.running_time:.2f} seconds, {self.action_count} actions and {self.turn_count} turns.")
        lines.append(f"Winner: Player {self.terminal_state.get_winner()}" if self.terminal_state.is_terminal_state() else "No winner")
        lines.append(f"{self.terminal_state}")

        return "\n".join(lines)
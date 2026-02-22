import time

from typing import Self

from tabulate import tabulate

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
    
    def summarise_game(self) -> str:
        lines = ["#### Outcome Observations ####"]
        lines.append(f"Episode ended after {self.running_time:.2f} seconds, {self.action_count} actions and {self.turn_count} turns.")
        lines.append(f"Winner: Player {self.terminal_state.get_winner()}" if self.terminal_state.is_terminal_state() else "No winner")
        lines.append(f"{self.terminal_state}")

        return "\n".join(lines)
    
    """Class methods for collecting and summarising aggregate outcome data for experimental anlaysis """

    @classmethod
    def get_winner_distributions(cls, observers: list[Self]) -> list[list]:
        """Return list of [player_id, 1st, 2nd, 3rd, 4th, stalemate, win rate, average finish position] for each player."""
        rows = [[i, 0, 0, 0, 0, 0, 0.0, 0.0] for i in range(len(observers[0].player_telemetries))]

        for observer in observers:
            finish_order = sorted(observer.player_telemetries, key=lambda x: (x.eliminated_turn_count is None, -(x.eliminated_turn_count or 0)))
            for i, player_telemetry in enumerate(finish_order):
                if player_telemetry.eliminated_turn_count is None and not observer.terminal_state.is_terminal_state():
                    rows[player_telemetry.player_id][5] += 1 # stalemate
                else:
                    rows[player_telemetry.player_id][i + 1] += 1 # 1st, 2nd, 3rd or 4th place

        for row in rows:
            row[6] = row[1] / len(observers) * 100 # win rate
            row[7] = sum((i * row[i] for i in range(1, 5))) / len(observers) # average finish position
        
        print(rows)
        return rows
    
    @classmethod
    def summarise_simulation(cls, observers: list[Self]) -> str:
        # Record 1st, 2nd and nth place counts for each player across all episodes,
        lines = ["#### Outcome Simulation Summary ####"]

        # Add winner distribution summaries
        lines.append(f"\n---- Winner Distribution Statistics ----")
        headers = [
            "Player",
            "1st",
            "2nd",
            "3rd",
            "4th",
            "Stalemate",
            "Win\nrate (%)",
            "Average\nfinish\nposition"
        ]
        lines.append(tabulate(cls.get_winner_distributions(observers), headers=headers, tablefmt="grid", colalign=["center"]*len(headers)))
        
        return "\n".join(lines)
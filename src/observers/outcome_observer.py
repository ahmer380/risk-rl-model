import time

from typing import Self

from tabulate import tabulate

from src.environment.game_state import GameState

from src.observers.observer import Observer, CoreObserver

class OutcomeObserver(Observer):
    """Observer for tracking the outcome of the game, including the winner and final game state."""
    def __init__(self, core_observer: CoreObserver):
        super().__init__(core_observer)

        self.terminal_state: GameState = None
        self.running_time: float = None
    
    def on_game_start(self):
        self.running_time = time.time()
        
    def on_game_end(self, terminal_state: GameState):
        self.running_time = time.time() - self.running_time
        self.terminal_state = terminal_state
    
    def summarise_game(self) -> str:
        lines = ["#### Outcome Observations ####"]
        lines.append(f"Episode ended after {self.running_time:.2f} seconds, {self.core_observer.action_count} actions and {self.core_observer.turn_count} turns.")
        lines.append(f"Winner: Player {self.terminal_state.get_winner()}" if self.terminal_state.is_terminal_state() else "No winner")
        lines.append(f"{self.terminal_state}")

        return "\n".join(lines)
    
    """Class methods for collecting and summarising aggregate outcome data for experimental anlaysis """
    
    @classmethod
    def summarise_simulation(cls, observers: list[Self]) -> str:
        lines = ["#### Outcome Simulation Summary ####"]

        # Add game length summaries
        lines.append(f"\n---- Game Length Statistics ----")
        headers = ["Metric", "Total", "Average", "Maximum", "Minimum"]
        lines.append(tabulate(cls.get_game_length_statistics(observers), headers=headers, tablefmt="grid", colalign=["center"]*len(headers)))

        # Add winner distribution summaries
        lines.append(f"\n---- Winner Distribution Statistics ----")
        headers = ["Player", "1st", "2nd", "3rd", "4th", "Stalemate", "Win\nrate (%)", "Average\nfinish\nposition"]
        lines.append(tabulate(cls.get_winner_distributions(observers), headers=headers, tablefmt="grid", colalign=["center"]*len(headers)))
        
        return "\n".join(lines)
    
    @classmethod
    def get_game_length_statistics(cls, observers: list[Self]) -> list:
        """Return list of [total, average, max, min] game length in seconds and turns."""
        rows = []

        action_counts = [observer.core_observer.action_count for observer in observers]
        rows.append(["Action count", sum(action_counts), round(sum(action_counts) / len(action_counts)), max(action_counts), min(action_counts)])

        turn_counts = [observer.core_observer.turn_count for observer in observers]
        rows.append(["Turn count", sum(turn_counts), round(sum(turn_counts) / len(turn_counts)), max(turn_counts), min(turn_counts)])

        running_times = [round(observer.running_time, 2) for observer in observers]
        rows.append(["Running time (s)", sum(running_times), round(sum(running_times) / len(running_times), 2), max(running_times), min(running_times)])
        
        return rows
    
    @classmethod
    def get_winner_distributions(cls, observers: list[Self]) -> list[list]:
        """Return list of [player_id, 1st, 2nd, 3rd, 4th, stalemate, win rate, average finish position] for each player."""
        rows = [[i, 0, 0, 0, 0, 0, 0.0, 0.0] for i in range(len(observers[0].core_observer.player_telemetries))]

        for observer in observers:
            finish_order = sorted(observer.core_observer.player_telemetries, key=lambda x: (x.eliminated_turn_count is not None, -(x.eliminated_turn_count or 0)))
            for i, player_telemetry in enumerate(finish_order):
                if player_telemetry.eliminated_turn_count is None and not observer.terminal_state.is_terminal_state():
                    rows[player_telemetry.player_id][5] += 1 # stalemate
                else:
                    rows[player_telemetry.player_id][i + 1] += 1 # 1st, 2nd, 3rd or 4th place

        for row in rows:
            row[6] = row[1] / len(observers) * 100 # win rate
            row[7] = sum((i * row[i] for i in range(1, 5))) / len(observers) # average finish position
        
        return rows
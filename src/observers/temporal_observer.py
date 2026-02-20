from tabulate import tabulate

from src.environment.actions import Action, ActionList, DeployAction, TradeAction, BattleAction, TransferAction, FortifyAction, SkipAction
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap

from src.observers.observer import Observer
from src.observers.player_telemetry import PlayerTelemetry

class TemporalObserver(Observer):
    """Observer for tracking performance of game implementation mechanics, intended for debugging use only."""
    def __init__(self, risk_map: RiskMap, player_telemetries: list[PlayerTelemetry]):
        super().__init__(risk_map, player_telemetries)
        
        self.action_counts_this_turn = {
            DeployAction.get_name(): 0,
            TradeAction.get_name(): 0,
            BattleAction.get_name(): 0,
            TransferAction.get_name(): 0,
            FortifyAction.get_name(): 0,
            SkipAction.get_name(): 0
        } # key=action_type, value=(maximum) count of actions of action_type taken in the current turn
    
    def on_action_list_generated(self, action_list: ActionList):
        for action_type in self.action_counts_this_turn.keys():
            self.action_counts_this_turn[action_type] = max(self.action_counts_this_turn[action_type], len(action_list.get_action_type_list_by_name(action_type)))
    
    def on_action_taken(self, _: Action, previous_state: GameState, current_state: GameState):
        if previous_state.current_phase == GamePhase.FORTIFY and current_state.current_phase == GamePhase.DRAFT:
            for action_type, count in self.action_counts_this_turn.items():
                self.player_telemetries[previous_state.current_player].action_counts_per_turn[action_type].append(count)
                self.action_counts_this_turn[action_type] = 0

    def summarise(self) -> str:
        lines = ["#### Temporal Statistics ####"]

        headers = [
            "Player",
            "Total\nturns",
            "Total\nactions",
            "Average\nactions",
            "Total\ndeploy\nactions",
            "Average\ndeploy\nactions",
            "Total\ntrade\nactions",
            "Average\ntrade\nactions",
            "Total\nbattle\nactions",
            "Average\nbattle\nactions",
            "Total\ntransfer\nactions",
            "Average\ntransfer\nactions",
            "Total\nfortify\nactions",
            "Average\nfortify\nactions",
            "Total\nskip\nactions",
            "Average\nskip\nactions"
        ]

        rows = []
        for player_telemetry in self.player_telemetries:
            total_turns = len(player_telemetry.action_counts_per_turn[DeployAction.get_name()]) # Each list in action_counts_per_turn should have the same length
            
            row = []
            row.append(f"Player {player_telemetry.player_id}")
            row.append(total_turns)
            row.append(sum(sum(counts) for counts in player_telemetry.action_counts_per_turn.values()))
            row.append(sum(sum(counts) for counts in player_telemetry.action_counts_per_turn.values()) / total_turns if total_turns > 0 else 0)
            row.append(sum(player_telemetry.action_counts_per_turn[DeployAction.get_name()]))
            row.append(sum(player_telemetry.action_counts_per_turn[DeployAction.get_name()]) / total_turns if total_turns > 0 else 0)
            row.append(sum(player_telemetry.action_counts_per_turn[TradeAction.get_name()]))
            row.append(sum(player_telemetry.action_counts_per_turn[TradeAction.get_name()]) / total_turns if total_turns > 0 else 0)
            row.append(sum(player_telemetry.action_counts_per_turn[BattleAction.get_name()]))
            row.append(sum(player_telemetry.action_counts_per_turn[BattleAction.get_name()]) / total_turns if total_turns > 0 else 0)
            row.append(sum(player_telemetry.action_counts_per_turn[TransferAction.get_name()]))
            row.append(sum(player_telemetry.action_counts_per_turn[TransferAction.get_name()]) / total_turns if total_turns > 0 else 0)
            row.append(sum(player_telemetry.action_counts_per_turn[FortifyAction.get_name()]))
            row.append(sum(player_telemetry.action_counts_per_turn[FortifyAction.get_name()]) / total_turns if total_turns > 0 else 0)
            row.append(sum(player_telemetry.action_counts_per_turn[SkipAction.get_name()]))
            row.append(sum(player_telemetry.action_counts_per_turn[SkipAction.get_name()]) / total_turns if total_turns > 0 else 0)
            rows.append(row)

        lines.append(tabulate(rows, headers=headers, tablefmt="grid", colalign=["center"]*len(headers)))

        return "\n".join(lines)

# TODO 1. Plot action_count-turn_count graph for each action_type per player (n graphs, 6 lines per graph)
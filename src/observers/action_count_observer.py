from tabulate import tabulate

from src.environment.actions import Action, ActionList, DeployAction, TradeAction, BattleAction, TransferAction, FortifyRouteAction, FortifyAmountAction, SkipAction
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap

from src.observers.observer import Observer
from src.observers.player_telemetry import PlayerTelemetry

class ActionCountObserver(Observer):
    """Observer for counting the distribution of actions generated and executed during a game."""
    def __init__(self, risk_map: RiskMap, player_telemetries: list[PlayerTelemetry]):
        super().__init__(risk_map, player_telemetries)
        
        self.action_counts_this_turn = {
            DeployAction.get_name(): [0, 0],
            TradeAction.get_name(): [0, 0],
            BattleAction.get_name(): [0, 0],
            TransferAction.get_name(): [0, 0],
            FortifyRouteAction.get_name(): [0, 0],
            FortifyAmountAction.get_name(): [0, 0],
            SkipAction.get_name(): [0, 0]
        } # key=action_type, value=((maximum) no.action_types generated, no.action_types executed) for the current turn
    
    def on_action_list_generated(self, action_list: ActionList):
        for action_type in self.action_counts_this_turn.keys():
            self.action_counts_this_turn[action_type][0] = max(self.action_counts_this_turn[action_type][0], len(action_list.get_action_type_list_by_name(action_type)))
    
    def on_action_taken(self, action: Action, previous_state: GameState, current_state: GameState):
        self.action_counts_this_turn[action.get_name()][1] += 1

        if previous_state.current_phase == GamePhase.FORTIFY and current_state.current_phase == GamePhase.DRAFT:
                self.push_action_counts_this_turn(previous_state.current_player)
    
    def on_game_end(self, terminal_state: GameState):
        self.push_action_counts_this_turn(terminal_state.current_player)
    
    def push_action_counts_this_turn(self, current_player: int):
        for action_type, (generated_count, executed_count) in self.action_counts_this_turn.items():
            self.player_telemetries[current_player].action_counts[action_type][0].append(generated_count)
            self.player_telemetries[current_player].action_counts[action_type][1].append(executed_count)
            self.action_counts_this_turn[action_type] = [0, 0]

    def summarise(self) -> str:
        lines = ["#### Action Count Observations ####"]

        # Add action generation counting summaries
        lines.append(f"\n---- Action Generation Counting Statistics ----")
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
            "Total\nfortify\nroute\nactions",
            "Average\nfortify\nroute\nactions",
            "Total\nfortify\namount\nactions",
            "Average\nfortify\namount\nactions",
            "Total\nskip\nactions",
            "Average\nskip\nactions"
        ]
        rows = []
        for player_telemetry in self.player_telemetries:
            total_turns = len(player_telemetry.action_counts[DeployAction.get_name()][0]) # same length for all action type lists
            row = []
            row.append(f"Player {player_telemetry.player_id}")
            row.append(total_turns)
            row.append(sum(sum(counts[0]) for counts in player_telemetry.action_counts.values()))
            row.append(sum(sum(counts[0]) for counts in player_telemetry.action_counts.values()) / total_turns if total_turns > 0 else 0)
            for action_counts in player_telemetry.action_counts.values():
                row.append(sum(action_counts[0]))
                row.append(sum(action_counts[0]) / total_turns if total_turns > 0 else 0)
            rows.append(row)
        lines.append(tabulate(rows, headers=headers, tablefmt="grid", colalign=["center"]*len(headers)))

        # Add action execution counting summaries
        lines.append(f"\n---- Action Execution Counting Statistics ----")
        rows = []
        for player_telemetry in self.player_telemetries:
            total_turns = len(player_telemetry.action_counts[DeployAction.get_name()][1]) # same length for all action type lists
            row = []
            row.append(f"Player {player_telemetry.player_id}")
            row.append(total_turns)
            row.append(sum(sum(counts[1]) for counts in player_telemetry.action_counts.values()))
            row.append(sum(sum(counts[1]) for counts in player_telemetry.action_counts.values()) / total_turns if total_turns > 0 else 0)
            for action_counts in player_telemetry.action_counts.values():
                row.append(sum(action_counts[1]))
                row.append(sum(action_counts[1]) / total_turns if total_turns > 0 else 0)
            rows.append(row)
        lines.append(tabulate(rows, headers=headers, tablefmt="grid", colalign=["center"]*len(headers)))
        
        return "\n".join(lines)

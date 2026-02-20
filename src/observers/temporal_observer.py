from src.environment.actions import DeployAction, TradeAction, BattleAction, TransferAction, FortifyAction, SkipAction
from src.environment.map import RiskMap

from src.observers.observer import Observer
from src.observers.player_telemetry import PlayerTelemetry

class TemporalObserver(Observer):
    """Observer for tracking performance of game implementation mechanics, intended for debugging use only."""
    def __init__(self, risk_map: RiskMap, player_telemetries: list[PlayerTelemetry]):
        super().__init__(risk_map, player_telemetries)
        
        self.action_counts_per_turn = {
            DeployAction.get_name(): [],
            TradeAction.get_name(): [],
            BattleAction.get_name(): [],
            TransferAction.get_name(): [],
            FortifyAction.get_name(): [],
            SkipAction.get_name(): []
        } #key=action_type, value=list of action counts indexed per turn
    
    def summarise(self):
        lines = []
        lines.append(f"\n#### Temporal Statistics ####")

# TODO 1. Plot action_count-turn_count graph for each action_type per player (n graphs, 6 lines per graph)
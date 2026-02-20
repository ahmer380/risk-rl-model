
from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState
from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.observer import Observer
from src.observers.outcome_observer import OutcomeObserver
from src.observers.player_telemetry import PlayerTelemetry
from src.observers.temporal_observer import TemporalObserver

class ObserverManager():
    """Manages multiple observers and notifies them of game events."""
    def __init__(
        self,
        risk_map: RiskMap,
        num_players: int,
        enable_outcome_observer = False,
        enable_battle_observer = False,
        enable_temporal_observer = False
    ):
        self.observers: list[Observer] = []
        
        player_telemetries = [PlayerTelemetry(i) for i in range(num_players)]
        if enable_outcome_observer:
            self.observers.append(OutcomeObserver(risk_map, player_telemetries))
        if enable_battle_observer:
            self.observers.append(BattleObserver(risk_map, player_telemetries))
        if enable_temporal_observer:
            self.observers.append(TemporalObserver(risk_map, player_telemetries))
    
    def notify_game_start(self):
        for observer in self.observers:
            observer.on_game_start()
    
    def notify_action_list_generated(self, action_list: ActionList):
        for observer in self.observers:
            observer.on_action_list_generated(action_list)
    
    def notify_action_taken(self, action: Action, previous_state: GameState, current_state: GameState):
        for observer in self.observers:
            observer.on_action_taken(action, previous_state, current_state)
    
    def notify_game_end(self, terminal_state: GameState):
        for observer in self.observers:
            observer.on_game_end(terminal_state)
    
    def summarise(self):
        for observer in self.observers:
            print(observer.summarise() + "\n")
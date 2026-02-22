
from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState
from src.environment.map import RiskMap

from src.observers.action_count_observer import ActionCountObserver
from src.observers.battle_observer import BattleObserver
from src.observers.observer import Observer, CoreObserver
from src.observers.outcome_observer import OutcomeObserver
from src.observers.player_telemetry import PlayerTelemetry

class ObserverManager():
    """Manages multiple observers and notifies them of game events for a single episode of Risk."""
    def __init__(
        self,
        risk_map: RiskMap,
        num_players: int,
        enable_outcome_observer = False,
        enable_battle_observer = False,
        enable_temporal_observer = False
    ):
        self.observers: list[Observer] = []
        
        if enable_outcome_observer or enable_battle_observer or enable_temporal_observer:
            core_observer = CoreObserver(risk_map, [PlayerTelemetry(i) for i in range(num_players)])
            self.observers.append(core_observer)

            if enable_outcome_observer:
                self.observers.append(OutcomeObserver(core_observer))
            if enable_battle_observer:
                self.observers.append(BattleObserver(core_observer))
            if enable_temporal_observer:
                self.observers.append(ActionCountObserver(core_observer))
    
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
    
    def summarise_game(self):
        for observer in self.observers:
            print(observer.summarise_game() + "\n")
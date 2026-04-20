from src.agents.agent import Agent

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState
from src.environment.map import RiskMap

from src.observers.observer import Observer, CoreObserver
from src.observers.player_telemetry import PlayerTelemetry

class ObserverManager():
    """Manages multiple observers and notifies them of game events for a single episode of Risk."""
    def __init__(
        self,
        risk_map: RiskMap,
        agents: list[Agent], # Already ordered by their turn_number for this game
        observers: list[Observer] = [],
    ):
        assert CoreObserver not in [type(observer) for observer in observers], "CoreObserver is automatically added and should not be included in the observer list."

        self.observers: list[Observer] = observers
        if self.observers:
            core_observer = CoreObserver(risk_map, [PlayerTelemetry(agent.get_name(), turn_number) for turn_number, agent in enumerate(agents)])
            for observer in self.observers:
                observer.core_observer = core_observer
            self.observers.insert(0, core_observer)
    
    def notify_game_start(self):
        for observer in self.observers:
            assert isinstance(observer, CoreObserver) or observer.core_observer is not None, "CoreObserver must be defined for each observer before the game starts."
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
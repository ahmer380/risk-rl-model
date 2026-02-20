from typing import Tuple

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState
from src.environment.map import RiskMap

class RiskEnvironment:
    def __init__(self, risk_map: RiskMap, num_players: int):
        self.map = risk_map
        self.num_players = num_players
        self.current_state = GameState(num_players, len(risk_map.territories), True)

    def step(self, action: Action) -> Tuple[GameState, float, bool]: # Returns (new_state, reward, is_terminal_state)
        previous_state = self.current_state
        self.current_state = action.apply(self.current_state, self.map)

        return (self.current_state, self.compute_reward(previous_state), self.current_state.is_terminal_state()) 
    
    def compute_reward(self, previous_state: GameState) -> float:
        if self.current_state.is_terminal_state():
            return 1.0
        
        return 0.0

    def reset(self):
        self.current_state.reset_to_initial_state()
    
    def get_action_list(self) -> ActionList:
        return ActionList.get_action_list(self.current_state, self.map)

from src.agents.agent import Agent

from src.environment.actions import Action, ActionList
from src.environment.map import RiskMap

from src.environment.game_state import GameState

class RLAgent(Agent):
    def __init__(self, risk_ppo):
        self.risk_ppo = risk_ppo

    def select_action(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> Action:
        assert risk_map.name == self.risk_ppo.map_name, "RLAgent is not compatible with the given map"
        
        return self.risk_ppo.predict(valid_actions, game_state)
    
    @classmethod
    def get_colour(cls):
        return "black"

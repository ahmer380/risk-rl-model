from src.agents.agent import Agent

from src.environment.actions import Action, ActionList
from src.environment.map import RiskMap

from src.environment.game_state import GameState

from src.train.ppo import RiskPPO

class RLAgent(Agent):
    def __init__(self, risk_map: RiskMap, num_players: int, version: int):
        super().__init__(draft_strategy=None, attack_strategy=None, fortify_strategy=None)
        self.risk_ppo = RiskPPO.load(risk_map, num_players, version)

    def select_action(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> Action:
        assert risk_map.name == self.risk_ppo.risk_map.name, "RLAgent is not compatible with the given map"
        
        return self.risk_ppo.predict(valid_actions, game_state)
    
    def get_name(self) -> str:
        return f"RLAgent"
    
    @classmethod
    def get_colour(cls):
        return "black"

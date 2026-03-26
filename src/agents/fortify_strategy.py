from abc import ABC

from src.agents.strategy import Strategy

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState
from src.environment.map import RiskMap

class FortifyStrategy(Strategy, ABC):
    pass

class RandomFortifyStrategy(FortifyStrategy):
    def select_action(self, valid_actions: ActionList, _game_state: GameState, _risk_map: RiskMap) -> Action:
        return valid_actions.get_random_action()
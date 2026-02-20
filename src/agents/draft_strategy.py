import random

from abc import ABC

from src.agents.strategy import Strategy

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState

class DraftStrategy(Strategy, ABC):
    pass

class RandomDraftStrategy(DraftStrategy):
    def select_action(self, valid_actions: ActionList, _: GameState) -> Action:
        return valid_actions.get_random_action()
    
class MinimumDraftStrategy(DraftStrategy):
    def select_action(self, valid_actions: ActionList, game_state: GameState) -> Action:
        """Deploy to the territory with the fewest troops."""
        if valid_actions.deploy_actions:
            return min(valid_actions.deploy_actions, key=lambda action: game_state.territory_troops[action.territory_id])
        else:
            return random.choice(valid_actions.trade_actions + valid_actions.skip_actions)

class MaximumDraftStrategy(DraftStrategy):
    def select_action(self, valid_actions: ActionList, game_state: GameState) -> Action:
        """Deploy to the territory with the most troops."""
        if valid_actions.deploy_actions:
            return max(valid_actions.deploy_actions, key=lambda action: game_state.territory_troops[action.territory_id])
        else:
            return random.choice(valid_actions.trade_actions + valid_actions.skip_actions)
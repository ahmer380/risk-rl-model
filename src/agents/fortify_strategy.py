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

class MinimumFortifyStrategy(FortifyStrategy):
    def select_action(self, valid_actions: ActionList, game_state: GameState, _risk_map: RiskMap) -> Action:
        """Select the fortify action that splits troops from the most populous territory to the least populous territory."""
        if valid_actions.fortify_route_actions:
            return max(valid_actions.fortify_route_actions, key=lambda action: game_state.territory_troops[action.from_territory_id] - game_state.territory_troops[action.to_territory_id])
        elif valid_actions.fortify_amount_actions:
            troop_count = max(max(action.troop_count for action in valid_actions.fortify_amount_actions) // 2, 1)
            return next(action for action in valid_actions.fortify_amount_actions if action.troop_count == troop_count)
        elif valid_actions.skip_actions:
            return valid_actions.skip_actions[0]
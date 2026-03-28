import random

from abc import ABC

from src.agents.strategy import Strategy

from src.environment.actions import Action, ActionList, FortifyAmountAction
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
            return FortifyAmountAction(troop_count)
        elif valid_actions.skip_actions:
            return valid_actions.skip_actions[0]

class MaximumFortifyStrategy(FortifyStrategy):
    """Select the fortify action that moves all troops from a capital territory to any random non-capital territory."""
    def __init__(self, capitals: int):
        self.capitals = capitals

    def select_action(self, valid_actions: ActionList, game_state: GameState, _risk_map: RiskMap) -> Action:
        capital_territory_ids = self.get_capital_territory_ids(game_state)
        possible_fortify_route_actions = [action for action in valid_actions.fortify_route_actions if action.from_territory_id in capital_territory_ids and action.to_territory_id not in capital_territory_ids]
        
        if possible_fortify_route_actions:
            return random.choice(possible_fortify_route_actions)
        elif valid_actions.fortify_amount_actions:
            return max(valid_actions.fortify_amount_actions, key=lambda action: action.troop_count)
        elif valid_actions.skip_actions:
            return valid_actions.skip_actions[0]
    
    def get_capital_territory_ids(self, game_state: GameState) -> list[int]:
        player_owned_territory_ids = game_state.get_player_owned_territory_ids()

        if len(player_owned_territory_ids) <= self.capitals:
            return player_owned_territory_ids
        else:
            threshold_troop_count = sorted([game_state.territory_troops[territory_id] for territory_id in player_owned_territory_ids], reverse=True)[self.capitals - 1]
            return [territory_id for territory_id in player_owned_territory_ids if game_state.territory_troops[territory_id] >= threshold_troop_count]

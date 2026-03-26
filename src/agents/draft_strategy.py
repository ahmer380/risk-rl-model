import random

from abc import ABC

from src.agents.strategy import Strategy

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState
from src.environment.map import RiskMap

class DraftStrategy(Strategy, ABC):
    pass

class RandomDraftStrategy(DraftStrategy):
    """Select a random deploy, trade, or skip action."""
    def select_action(self, valid_actions: ActionList, _game_state: GameState, _risk_map: RiskMap) -> Action:
        return valid_actions.get_random_action()
    
class MinimumDeployStrategy(DraftStrategy):
    """Deploy to the territory with the fewest troops."""
    def select_action(self, valid_actions: ActionList, game_state: GameState, _: RiskMap) -> Action:
        if valid_actions.deploy_actions:
            return min(valid_actions.deploy_actions, key=lambda action: game_state.territory_troops[action.territory_id])
        else:
            return random.choice(valid_actions.trade_actions + valid_actions.skip_actions)

class MaximumDeployStrategy(DraftStrategy):
    """Deploy to one of the top-capitals territories with the most troops."""
    def __init__(self, capitals: int):
        self.capitals = capitals
    
    def select_action(self, valid_actions: ActionList, game_state: GameState, _: RiskMap) -> Action:
        if valid_actions.deploy_actions:
            if len(valid_actions.deploy_actions) <= self.capitals:
                capital_deploy_actions = valid_actions.deploy_actions
            else:
                sorted_actions_by_troop_count = sorted(valid_actions.deploy_actions, key=lambda action: game_state.territory_troops[action.territory_id], reverse=True)
                capital_deploy_actions = [action for action in valid_actions.deploy_actions if game_state.territory_troops[action.territory_id] >= game_state.territory_troops[sorted_actions_by_troop_count[self.capitals - 1].territory_id]]

            return random.choice(capital_deploy_actions)
        else:
            return random.choice(valid_actions.trade_actions + valid_actions.skip_actions)

class ContinentalDeployStrategy(DraftStrategy):
    """Deploy to a territory inside a continent the player has the most current control over."""
    def select_action(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> Action:
        if valid_actions.deploy_actions:
            continent_c_scores = self.get_continent_c_scores(game_state.get_player_owned_territory_ids(), risk_map)
            max_c_score_continent = continent_c_scores.index(max(continent_c_scores))
            territories_in_most_controlled_continent = [action for action in valid_actions.deploy_actions if risk_map.territories[action.territory_id].continent.id == max_c_score_continent]

            return random.choice(territories_in_most_controlled_continent)
        else:
            return random.choice(valid_actions.trade_actions + valid_actions.skip_actions)
    
    def get_continent_c_scores(self, player_owned_territory_ids: list[int], risk_map: RiskMap) -> list[float]:
        """Return a list of c-scores for each continent indexed by continent_id"""
        c_scores = [0.0] * len(risk_map.continents)
        for territory_id in player_owned_territory_ids:
            c_scores[risk_map.territories[territory_id].continent.id] += 1
        
        for continent in risk_map.continents.values():
            c_scores[continent.id] /= len(continent.territories)
        
        return c_scores

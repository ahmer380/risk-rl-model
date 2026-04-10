import random

from abc import ABC, abstractmethod

from src.agents.strategy import Strategy

from src.environment.actions import Action, ActionList, FortifyFromAction, FortifyToAction, FortifyAmountAction, MAX_TROOP_TRANSFER
from src.environment.game_state import GameState
from src.environment.map import RiskMap

class FortifyStrategy(Strategy, ABC):
    def __init__(self):
        self.best_fortify: tuple[FortifyFromAction, FortifyToAction, FortifyAmountAction] = None

    def select_action(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> Action:
        if valid_actions.fortify_from_actions:
            self.best_fortify = self.compute_best_fortify(valid_actions, game_state, risk_map)
            if not self.best_fortify:
                return valid_actions.skip_actions[0]
            else:
                return self.best_fortify[0]
        elif valid_actions.fortify_to_actions:
            return self.best_fortify[1]
        elif valid_actions.fortify_amount_actions:
            fortify_amount_action = self.best_fortify[2]
            self.best_fortify = None

            return fortify_amount_action
        elif valid_actions.skip_actions:
            return valid_actions.skip_actions[0]
        else:
            raise ValueError("No valid fortifying actions available, but the fortify strategy was called")

    @abstractmethod
    def compute_best_fortify(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> tuple[FortifyFromAction, FortifyToAction, FortifyAmountAction]:
        """Computes the best fortify action to take based on the current position, or None if a skip action should be taken instead."""

class RandomFortifyStrategy(FortifyStrategy):
    def compute_best_fortify(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> tuple[FortifyFromAction, FortifyToAction, FortifyAmountAction]:
        selected_fortify_from_action = random.choice(valid_actions.fortify_from_actions)
        forwarded_game_state = selected_fortify_from_action.apply(game_state, risk_map)
        selected_fortify_to_action = random.choice(FortifyToAction.get_action_list(forwarded_game_state, risk_map))
        forwarded_game_state = selected_fortify_to_action.apply(forwarded_game_state, risk_map)
        selected_fortify_amount_action = random.choice(FortifyAmountAction.get_action_list(forwarded_game_state, risk_map))

        return (selected_fortify_from_action, selected_fortify_to_action, selected_fortify_amount_action)

class MinimumFortifyStrategy(FortifyStrategy):
    def compute_best_fortify(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> tuple[FortifyFromAction, FortifyToAction, FortifyAmountAction]:
        """Select the fortify action that splits troops from the most populous territory to the least populous territory."""
        best_fortify_route: tuple[FortifyFromAction, FortifyToAction] = None

        for fortify_from_action in valid_actions.fortify_from_actions:
            forwarded_game_state = fortify_from_action.apply(game_state, risk_map)
            least_fortified_territory = min(FortifyToAction.get_action_list(forwarded_game_state, risk_map), key=lambda to_action: game_state.territory_troops[to_action.to_territory_id])
            if not best_fortify_route or game_state.territory_troops[fortify_from_action.from_territory_id] - game_state.territory_troops[least_fortified_territory.to_territory_id] > game_state.territory_troops[best_fortify_route[0].from_territory_id] - game_state.territory_troops[best_fortify_route[1].to_territory_id]:
                best_fortify_route = (fortify_from_action, least_fortified_territory)
        
        troop_count = max((game_state.territory_troops[best_fortify_route[0].from_territory_id] - game_state.territory_troops[best_fortify_route[1].to_territory_id]) // 2, 1)

        return (best_fortify_route[0], best_fortify_route[1], FortifyAmountAction(troop_count))

class MaximumFortifyStrategy(FortifyStrategy):
    """Select the fortify action that moves all troops from a capital territory to any random non-capital territory."""
    def __init__(self, capitals: int):
        self.capitals = capitals

    def compute_best_fortify(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> tuple[FortifyFromAction, FortifyToAction, FortifyAmountAction]:
        possible_fortify_routes: list[tuple[FortifyFromAction, FortifyToAction]] = []
        capital_territory_ids = self.get_capital_territory_ids(game_state)
        
        for fortify_from_action in valid_actions.fortify_from_actions:
            if fortify_from_action.from_territory_id in capital_territory_ids:
                forwarded_game_state = fortify_from_action.apply(game_state, risk_map)
                for fortify_to_action in FortifyToAction.get_action_list(forwarded_game_state, risk_map):
                    if fortify_to_action.to_territory_id not in capital_territory_ids:
                        possible_fortify_routes.append((fortify_from_action, fortify_to_action))

        if possible_fortify_routes:
            best_fortify_route = random.choice(possible_fortify_routes)

            return (best_fortify_route[0], best_fortify_route[1], FortifyAmountAction(MAX_TROOP_TRANSFER))
        else:
            return None
    
    def get_capital_territory_ids(self, game_state: GameState) -> list[int]:
        player_owned_territory_ids = game_state.get_player_owned_territory_ids()

        if len(player_owned_territory_ids) <= self.capitals:
            return player_owned_territory_ids
        else:
            threshold_troop_count = sorted([game_state.territory_troops[territory_id] for territory_id in player_owned_territory_ids], reverse=True)[self.capitals - 1]
            return [territory_id for territory_id in player_owned_territory_ids if game_state.territory_troops[territory_id] >= threshold_troop_count]

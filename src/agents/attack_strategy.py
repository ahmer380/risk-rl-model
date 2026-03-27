import random

from enum import Enum

from abc import ABC

from src.agents.strategy import Strategy

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState
from src.environment.map import RiskMap

class TransferMethod(Enum):
    RANDOM = 0
    ONE = 1
    ALL = 2
    SPLIT = 3

class AttackStrategy(Strategy, ABC):
    def __init__(self, transfer_method: TransferMethod):
        self.transfer_method = transfer_method

    def select_non_battle_action(self, valid_actions: ActionList) -> Action:
        """Either selects a transfer action based on the specified transfer method or a skip action."""
        if valid_actions.skip_actions and not valid_actions.transfer_actions:
            return valid_actions.skip_actions[0]  # Exactly one of these will be available, not more or less
        elif valid_actions.transfer_actions and not valid_actions.skip_actions:
            if self.transfer_method == TransferMethod.RANDOM:
                return random.choice(valid_actions.transfer_actions)
            elif self.transfer_method == TransferMethod.ONE:
                return min(valid_actions.transfer_actions, key=lambda action: action.troop_count) # should be 1
            elif self.transfer_method == TransferMethod.ALL:
                return max(valid_actions.transfer_actions, key=lambda action: action.troop_count) # should be territory_troops[attacker] - 1
            elif self.transfer_method == TransferMethod.SPLIT:
                troop_count = max(max(action.troop_count for action in valid_actions.transfer_actions) // 2, 1)
                return next(action for action in valid_actions.transfer_actions if action.troop_count == troop_count)
        else:
            raise ValueError("Expected either transfer actions or skip actions to be available, but found both or neither.")

class WeightedRandomAttackStrategy(AttackStrategy):
    """Select a random battle, transfer, or skip action with a weighted probability."""
    def __init__(self, battle_weight: float):
        super().__init__(TransferMethod.RANDOM)
        self.battle_weight = battle_weight

    def select_action(self, valid_actions: ActionList, _game_state: GameState, _risk_map: RiskMap) -> Action:
        if valid_actions.battle_actions and random.random() < self.battle_weight:
            return random.choice(valid_actions.battle_actions)
        else:
            return self.select_non_battle_action(valid_actions)

class SafeBattleStrategy(AttackStrategy):
    def __init__(self, disparity: int, transfer_method: TransferMethod = TransferMethod.RANDOM):
        super().__init__(transfer_method)
        self.disparity = disparity

    def select_action(self, valid_actions: ActionList, game_state: GameState, _: RiskMap) -> Action:
        """Only initiates battles if the player has a significant advantage in the number of armies."""
        best_battle = max(valid_actions.battle_actions, key=lambda action: (game_state.territory_troops[action.attacker_territory_id] - game_state.territory_troops[action.defender_territory_id], game_state.territory_troops[action.attacker_territory_id]), default=None)

        if best_battle and game_state.territory_troops[best_battle.attacker_territory_id] - game_state.territory_troops[best_battle.defender_territory_id] >= self.disparity:
            return best_battle
        else:
            return self.select_non_battle_action(valid_actions)

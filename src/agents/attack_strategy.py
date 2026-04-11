import random

from abc import ABC, abstractmethod

from src.agents.strategy import Strategy

from src.environment.actions import TransferMethod, Action, ActionList, BattleFromAction, BattleToAction, TransferAction, SkipAction
from src.environment.game_state import GameState
from src.environment.map import RiskMap

class AttackStrategy(Strategy, ABC):
    def __init__(self, transfer_method: TransferMethod):
        self.transfer_method = transfer_method
        self.best_battle: tuple[BattleFromAction, BattleToAction] = None
    
    def select_action(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> Action:
        if valid_actions.battle_from_actions:
            self.best_battle = self.compute_best_battle(valid_actions, game_state, risk_map)
            if not self.best_battle:
                return SkipAction()
            else:
                return self.best_battle[0]
        elif valid_actions.battle_to_actions:
            battle_to_action = self.best_battle[1]
            self.best_battle = None

            return battle_to_action
        elif valid_actions.transfer_actions:
            return TransferAction(self.transfer_method)
        elif valid_actions.skip_actions:
            return valid_actions.skip_actions[0]
        else:
            raise ValueError("No valid attacking actions available, but the attack strategy was called")
    
    @abstractmethod
    def compute_best_battle(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> tuple[BattleFromAction, BattleToAction]:
        """Computes the best battle to initiate based on the current position, or None if a skip action should be taken instead."""

class WeightedRandomAttackStrategy(AttackStrategy):
    """Select a random battle, transfer, or skip action with a weighted probability."""
    def __init__(self, battle_weight: float):
        super().__init__(TransferMethod.RANDOM)
        self.battle_weight = battle_weight

    def compute_best_battle(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> tuple[BattleFromAction, BattleToAction]:
        if random.random() < self.battle_weight:
            selected_battle_from_action = random.choice(valid_actions.battle_from_actions)
            forwarded_game_state = selected_battle_from_action.apply(game_state, risk_map)
            selected_battle_to_action = random.choice(BattleToAction.get_action_list(forwarded_game_state, risk_map))

            return (selected_battle_from_action, selected_battle_to_action)
        else:
            return None

class SafeBattleStrategy(AttackStrategy):
    def __init__(self, disparity: int, transfer_method: TransferMethod = TransferMethod.RANDOM):
        super().__init__(transfer_method)
        self.disparity = disparity

    def compute_best_battle(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> tuple[BattleFromAction, BattleToAction]:
        best_battle: tuple[BattleFromAction, BattleToAction] = None

        for battle_from_action in valid_actions.battle_from_actions:
            forwarded_game_state = battle_from_action.apply(game_state, risk_map)
            least_defended_territory = min(BattleToAction.get_action_list(forwarded_game_state, risk_map), key=lambda to_action: game_state.territory_troops[to_action.defender_territory_id])

            if not best_battle or game_state.territory_troops[battle_from_action.attacker_territory_id] - game_state.territory_troops[least_defended_territory.defender_territory_id] > game_state.territory_troops[best_battle[0].attacker_territory_id] - game_state.territory_troops[best_battle[1].defender_territory_id]:
                best_battle = (battle_from_action, least_defended_territory)

        if best_battle and game_state.territory_troops[best_battle[0].attacker_territory_id] - game_state.territory_troops[best_battle[1].defender_territory_id] >= self.disparity:
            return best_battle
        else:
            return None

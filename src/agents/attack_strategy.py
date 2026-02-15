import random

from abc import ABC

from src.agents.strategy import Strategy

from src.environment.game_state import GameState
from src.environment.actions import Action, BattleAction, TransferAction, SkipAction

class AttackStrategy(Strategy, ABC):
    def segment_action_list(self, valid_actions) -> tuple[list[BattleAction], list[TransferAction], list[SkipAction]]: 
        battle_actions, transfer_actions, skip_actions = [], [], []

        for action in valid_actions:
            if isinstance(action, BattleAction):
                battle_actions.append(action)
            elif isinstance(action, TransferAction):
                transfer_actions.append(action)
            elif isinstance(action, SkipAction):
                skip_actions.append(action)
        
        return battle_actions, transfer_actions, skip_actions

class RandomAttackStrategy(AttackStrategy):
    def select_action(self, valid_actions: list[Action], _: GameState) -> Action:
        return random.choice(valid_actions)
    
class AdvantageAttackStrategy(AttackStrategy):
    def select_action(self, valid_actions: list[Action], game_state: GameState) -> Action:
        """Only initiates battles if the player has a significant advantage in the number of armies."""
        battle_actions, transfer_actions, skip_actions = self.segment_action_list(valid_actions)
        
        best_battle = max(battle_actions, key=lambda action: (game_state.territory_troops[action.attacker_territory_id] - game_state.territory_troops[action.defender_territory_id], game_state.territory_troops[action.attacker_territory_id]), default=None)

        if best_battle and game_state.territory_troops[best_battle.attacker_territory_id] - game_state.territory_troops[best_battle.defender_territory_id] >= 3:
            return best_battle
        else:
            return random.choice(transfer_actions + skip_actions)

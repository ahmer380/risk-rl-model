import random

from abc import ABC

from src.agents.strategy import Strategy

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState

class AttackStrategy(Strategy, ABC):
    pass

class RandomAttackStrategy(AttackStrategy):
    def select_action(self, valid_actions: ActionList, _: GameState) -> Action:
        return valid_actions.get_random_action()
    
class AdvantageAttackStrategy(AttackStrategy):
    def select_action(self, valid_actions: ActionList, game_state: GameState) -> Action:
        """Only initiates battles if the player has a significant advantage in the number of armies."""
        best_battle = max(valid_actions.battle_actions, key=lambda action: (game_state.territory_troops[action.attacker_territory_id] - game_state.territory_troops[action.defender_territory_id], game_state.territory_troops[action.attacker_territory_id]), default=None)

        if best_battle and game_state.territory_troops[best_battle.attacker_territory_id] - game_state.territory_troops[best_battle.defender_territory_id] >= 3:
            return best_battle
        else:
            return random.choice(valid_actions.transfer_actions + valid_actions.skip_actions)

class DisadvantageAttackStrategy(AttackStrategy):
    def select_action(self, valid_actions: ActionList, game_state: GameState) -> Action:
        """Initiates the battle with the worst odds."""
        worst_battle = min(valid_actions.battle_actions, key=lambda action: (game_state.territory_troops[action.attacker_territory_id] - game_state.territory_troops[action.defender_territory_id], game_state.territory_troops[action.attacker_territory_id]), default=None)

        if worst_battle:
            return worst_battle
        else:
            return random.choice(valid_actions.transfer_actions + valid_actions.skip_actions)

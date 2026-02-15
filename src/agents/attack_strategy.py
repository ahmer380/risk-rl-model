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
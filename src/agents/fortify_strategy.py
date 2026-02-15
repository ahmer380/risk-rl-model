import random

from abc import ABC

from src.agents.strategy import Strategy

from src.environment.game_state import GameState
from src.environment.actions import Action, FortifyAction, SkipAction

class FortifyStrategy(Strategy, ABC):
    def segment_action_list(self, valid_actions) -> tuple[list[FortifyAction], list[SkipAction]]:
        fortify_actions, skip_actions = [], []

        for action in valid_actions:
            if isinstance(action, FortifyAction):
                fortify_actions.append(action)
            elif isinstance(action, SkipAction):
                skip_actions.append(action)
        
        return fortify_actions, skip_actions

class RandomFortifyStrategy(FortifyStrategy):
    def select_action(self, valid_actions: list[Action], _: GameState) -> Action:
        return random.choice(valid_actions)
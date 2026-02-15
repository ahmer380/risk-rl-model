import random

from abc import ABC

from src.agents.strategy import Strategy

from src.environment.game_state import GameState
from src.environment.actions import Action, DeployAction, TradeAction, SkipAction

class DraftStrategy(Strategy, ABC):
    def segment_action_list(self, valid_actions) -> tuple[list[DeployAction], list[TradeAction], list[SkipAction]]: 
        deploy_actions, trade_actions, skip_actions = [], [], []

        for action in valid_actions:
            if isinstance(action, DeployAction):
                deploy_actions.append(action)
            elif isinstance(action, TradeAction):
                trade_actions.append(action)
            elif isinstance(action, SkipAction):
                skip_actions.append(action)
        
        return deploy_actions, trade_actions, skip_actions

class RandomDraftStrategy(DraftStrategy):
    def select_action(self, valid_actions: list[Action], _: GameState) -> Action:
        return random.choice(valid_actions)
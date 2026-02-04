from environment import actions
from src.environment.game_state import GameState
from src.environment.map import RiskMap
from src.environment.actions import Action, DeployAction, TradeAction, BattleAction, TransferAction, FortifyAction, SkipAction

class RiskEnvironment:
    def __init__(self, risk_map: RiskMap, num_players: int):
        self.map = risk_map
        self.num_players = num_players
        self.state = GameState(num_players, len(risk_map.territories))
    
    def get_action_list(self) -> list[Action]:
        action_types: list[Action] = [DeployAction, TradeAction, BattleAction, TransferAction, FortifyAction, SkipAction]
        return [action for action_type in action_types for action in action_type.get_action_list(self.state)]

    def reset(self, seed=None):
        if seed is not None:
            import random
            random.seed(seed)

        self.state.reset_to_initial_state()
        return self.state

    def step(self, action: Action):
        raise NotImplementedError

    def is_done(self):
        return self.state.is_terminal_state()

    def current_player(self):
        return self.state.current_player

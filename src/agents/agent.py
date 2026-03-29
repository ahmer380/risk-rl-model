from abc import ABC

from src.agents.draft_strategy import DraftStrategy, RandomDraftStrategy, MinimumDeployStrategy, MaximumDeployStrategy
from src.agents.attack_strategy import AttackStrategy, WeightedRandomAttackStrategy, SafeBattleStrategy, TransferMethod
from src.agents.fortify_strategy import FortifyStrategy, RandomFortifyStrategy, MinimumFortifyStrategy, MaximumFortifyStrategy

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap

class Agent(ABC):
    player_id: int = 0

    def __init__(self, draft_strategy: DraftStrategy, attack_strategy: AttackStrategy, fortify_strategy: FortifyStrategy):
        Agent.player_id += 1
        type(self).player_id += 1

        self.player_id = type(self).player_id
        self.draft_strategy = draft_strategy
        self.attack_strategy = attack_strategy
        self.fortify_strategy = fortify_strategy

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.player_id = 0

    def select_action(self, valid_actions: ActionList, game_state: GameState, risk_map: RiskMap) -> Action:
        """Select an action from the list of valid actions based on the current game state and the agent's policy."""
        if game_state.current_phase == GamePhase.DRAFT:
            return self.draft_strategy.select_action(valid_actions, game_state, risk_map)
        elif game_state.current_phase == GamePhase.ATTACK:
            return self.attack_strategy.select_action(valid_actions, game_state, risk_map)
        elif game_state.current_phase == GamePhase.FORTIFY:
            return self.fortify_strategy.select_action(valid_actions, game_state, risk_map)
    
    def reset(self):
        """Reset any internal state of the agent if necessary for the start of a new episode."""
    
    def get_name(self) -> str:
        """Return the name of the agent for logging and visualisation purposes."""
        if type(self).player_id == 1:
            return self.__class__.__name__
        else:
            return f"{self.__class__.__name__} {self.player_id}"
    
    @classmethod
    def reset_player_ids(cls):
        """Reset the player ID counter for all subclasses of Agent."""
        cls.player_id = 0

        for subclass in cls.__subclasses__():
            subclass.reset_player_ids()

class RandomAgent(Agent):
    """Selects a random action"""
    def __init__(self, battle_weight: float = 0.95):
        super().__init__(RandomDraftStrategy(), WeightedRandomAttackStrategy(battle_weight), RandomFortifyStrategy())

class CommunistAgent(Agent):
    """Prioritises each territory equally, deploying/fortifying to the territory with the fewest troops at a given time"""
    def __init__(self, disparity: int = 3):
        super().__init__(
            MinimumDeployStrategy(),
            SafeBattleStrategy(disparity=disparity, transfer_method=TransferMethod.SPLIT),
            MinimumFortifyStrategy()
        )

class CapitalistAgent(Agent):
    """Concentrates troops on a small set of strong territories."""
    def __init__(self, capitals: int = 3, disparity: int = 10):
        super().__init__(
            MaximumDeployStrategy(capitals),
            SafeBattleStrategy(disparity=disparity, transfer_method=TransferMethod.ALL),
            MaximumFortifyStrategy(capitals),
        )

from abc import ABC

from src.agents.draft_strategy import DraftStrategy, RandomDraftStrategy, MinimumDeployStrategy
from src.agents.attack_strategy import AttackStrategy, WeightedRandomAttackStrategy, SafeBattleStrategy, TransferMethod
from src.agents.fortify_strategy import FortifyStrategy, RandomFortifyStrategy, MinimumFortifyStrategy

from src.environment.actions import Action, ActionList
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap

class Agent(ABC):
    def __init__(self, player_id: int, draft_strategy: DraftStrategy, attack_strategy: AttackStrategy, fortify_strategy: FortifyStrategy):
        self.player_id = player_id
        self.draft_strategy = draft_strategy
        self.attack_strategy = attack_strategy
        self.fortify_strategy = fortify_strategy

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

class RandomAgent(Agent):
    """Selects a random action"""
    def __init__(self, player_id: int, battle_weight: float = 0.95):
        super().__init__(player_id, RandomDraftStrategy(), WeightedRandomAttackStrategy(battle_weight), RandomFortifyStrategy())

class CommunistAgent(Agent):
    """Prioritises each territory equally, deploying/fortifying to the territory with the fewest troops at a given time"""
    def __init__(self, player_id: int):
        super().__init__(player_id, MinimumDeployStrategy(), SafeBattleStrategy(3, TransferMethod.SPLIT), MinimumFortifyStrategy())
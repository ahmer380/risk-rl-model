from abc import ABC

from src.agents.draft_strategy import DraftStrategy, RandomDraftStrategy
from src.agents.attack_strategy import AttackStrategy, RandomAttackStrategy
from src.agents.fortify_strategy import FortifyStrategy, RandomFortifyStrategy

from src.environment.actions import Action
from src.environment.game_state import GameState, GamePhase

class Agent(ABC):
    def __init__(self, player_id: int, draft_strategy: DraftStrategy, attack_strategy: AttackStrategy, fortify_strategy: FortifyStrategy):
        self.player_id = player_id
        self.draft_strategy = draft_strategy
        self.attack_strategy = attack_strategy
        self.fortify_strategy = fortify_strategy

    def select_action(self, valid_actions: list[Action], game_state: GameState) -> Action:
        """Select an action from the list of valid actions based on the current game state and the agent's policy."""
        if game_state.current_phase == GamePhase.DRAFT:
            return self.draft_strategy.select_action(valid_actions, game_state)
        elif game_state.current_phase == GamePhase.ATTACK:
            return self.attack_strategy.select_action(valid_actions, game_state)
        elif game_state.current_phase == GamePhase.FORTIFY:
            return self.fortify_strategy.select_action(valid_actions, game_state)
    
    def reset(self):
        """Reset any internal state of the agent if necessary for the start of a new episode."""

class RandomAgent(Agent):
    def __init__(self, player_id: int):
        super().__init__(player_id, RandomDraftStrategy(), RandomAttackStrategy(), RandomFortifyStrategy())
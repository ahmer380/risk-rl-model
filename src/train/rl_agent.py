from src.environment.actions import Action

from src.environment.game_state import GameState

from src.agents.agent import Agent

class RLAgent(Agent):
    def __init__(self, player_id: int):
        self.player_id = player_id

    def select_action(self, valid_actions: list[Action], game_state: GameState) -> Action:
        pass
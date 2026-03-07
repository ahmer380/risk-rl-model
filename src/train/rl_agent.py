from src.agents.agent import Agent

from src.environment.actions import Action, ActionList

from src.environment.game_state import GameState

class RLAgent(Agent):
    def __init__(self, player_id: int, risk_ppo):
        self.player_id = player_id
        self.risk_ppo = risk_ppo

    def select_action(self, valid_actions: ActionList, game_state: GameState) -> Action:
        self.risk_ppo.gym_environment.game_state = game_state
        observation = self.risk_ppo.gym_environment.encode_observation()
        action, _ = self.risk_ppo.model.predict(observation, action_masks=self.risk_ppo.gym_environment.action_masks(valid_actions))
        decoded_action = self.risk_ppo.gym_environment.decode_action(action)

        return decoded_action
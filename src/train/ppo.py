from typing import Self

from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback

from src.environment.actions import Action, ActionList
from src.environment.map import RiskMap
from src.environment.game_state import GameState

from src.train.gym_environment import RiskGymEnvironment

class RiskPPO:
    """Trains a PPO agent to play Risk on a given map and number of players."""
    def __init__(self, risk_map: RiskMap, num_players: int):
        self.risk_map = risk_map
        self.num_players = num_players

        self.env = RiskGymEnvironment(
            risk_map=self.risk_map,
            num_players=self.num_players,
            max_episode_length=500
        )

        self.hyperparameters = dict(
            policy="MultiInputPolicy",
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=512,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
        )

        self.model = MaskablePPO(
            env=self.env,
            tensorboard_log=f"models/{self.risk_map.name}_map_{self.num_players}_player/logs",
            **self.hyperparameters,
        )
    
    def train(self, total_timesteps: int = 1_000_000):
        self.model.learn(total_timesteps=total_timesteps, progress_bar=True, callback=RiskMetricsCallback())
    
    def predict(self, valid_actions: ActionList, game_state: GameState) -> Action:
        self.env.game_state = game_state
        observation = self.env.encode_observation()
        action, _ = self.model.predict(observation=observation, action_masks=self.env.action_masks(valid_actions))
        decoded_action = self.env.decode_action(action)

        return decoded_action

    def save(self, version: int):
        self.model.save(f"models/{self.risk_map.name}_map_{self.num_players}_player/v{version}".lower())
    
    @classmethod
    def load(cls, risk_map: RiskMap, num_players: int, version: int) -> Self:
        risk_ppo = cls(risk_map, num_players)
        path = f"models/{risk_map.name}_map_{num_players}_player/v{version}".lower()
        risk_ppo.model = MaskablePPO.load(path, env=risk_ppo.env)

        return risk_ppo

class RiskMetricsCallback(BaseCallback):
    def _on_step(self):
        infos = self.locals["infos"]
        for info in infos:
            if "win" in info:
                self.logger.record("game/win_rate", info["win"])
                self.logger.record("game/episode_length", info["episode_length"])
        return True

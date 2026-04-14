from typing import Self

from pathlib import Path

from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback

from src.environment.actions import Action, ActionList
from src.environment.map import RiskMap
from src.environment.game_state import GameState

from src.train.gym_environment import RiskGymEnvironment

class RiskPPO:
    """Trains a PPO agent to play Risk on a given map and number of players."""
    def __init__(self, risk_map: RiskMap, num_players: int, model_name: str = None):
        self.risk_map = risk_map
        self.num_players = num_players

        if model_name is None:
            model_dir = Path(f"models/{self.risk_map.name}_map_{self.num_players}_player")
            most_recent_version = 0 if not model_dir.exists() else len(list(model_dir.glob("*.zip")))
            model_name = f"v{most_recent_version + 1}"
        self.model_name = model_name

        self.env = RiskGymEnvironment(
            risk_map=self.risk_map,
            num_players=self.num_players
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
        print(f"Training PPO agent on {self.risk_map.name} map with {self.num_players} players for {total_timesteps} timesteps...")
        self.model.learn(
            total_timesteps=total_timesteps,
            progress_bar=True,
            callback=RiskMetricsCallback(),
            tb_log_name=self.model_name,
        )
    
    def predict(self, valid_actions: ActionList, game_state: GameState) -> Action:
        self.env.game_state = game_state
        observation = self.env.encode_observation(inference=True)
        action, _ = self.model.predict(observation=observation, action_masks=self.env.action_masks(valid_actions))
        decoded_action = self.env.decode_action(action)

        return decoded_action

    def save(self):
        self.model.save(f"models/{self.risk_map.name}_map_{self.num_players}_player/{self.model_name}".lower())
    
    @classmethod
    def load(cls, risk_map: RiskMap, num_players: int, model_name: str = None) -> Self:
        if model_name is None:
            model_dir = Path(f"models/{risk_map.name}_map_{num_players}_player")
            most_recent_version = len(list(model_dir.glob("*.zip")))
            model_name = f"v{most_recent_version}"

        risk_ppo = cls(risk_map, num_players, model_name)
        path = f"models/{risk_map.name}_map_{num_players}_player/{risk_ppo.model_name}".lower()
        risk_ppo.model = MaskablePPO.load(path, env=risk_ppo.env)

        return risk_ppo

class RiskMetricsCallback(BaseCallback):
    def __init__(self):
        super().__init__()
        self.total_episodes = 0
        self.total_wins = 0

    def _on_step(self):
        infos = self.locals["infos"]
        for info in infos:
            if "win" in info:
                self.total_episodes += 1
                self.total_wins += 1 if info["win"] else 0
                self.logger.record("win_rate", self.total_wins / self.total_episodes)
                self.logger.record("average_episode_length", self.num_timesteps /self.total_episodes)
        return True

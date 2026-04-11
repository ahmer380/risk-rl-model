import torch.nn as nn

from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback

from src.agents.agent import CommunistAgent

from src.environment.actions import Action, ActionList
from src.environment.map import RiskMap
from src.environment.game_state import GameState

from src.train.gym_environment import RiskGymEnvironment
from src.train.rl_agent import RLAgent

class RiskPPO:
    """Trains a PPO agent to play Risk on a given map and number of players."""
    def __init__(self, map_name: str, num_players: int):
        self.map_name = map_name
        self.num_players = num_players

        agent_composition = [RLAgent(None)] + [CommunistAgent(disparity=0) for _ in range(num_players - 1)]
        self.env = RiskGymEnvironment(
            risk_map=RiskMap.from_json(f"maps/{map_name}.json"),
            agent_composition=agent_composition, 
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
            tensorboard_log=f"models/{self.map_name}_map_{self.num_players}_player/logs",
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

    def save(self, suffix: str):
        self.model.save(f"models/{self.map_name}_map_{self.num_players}_player/{suffix}")
    
    def load(self, suffix: str):
        path = f"models/{self.map_name}_map_{self.num_players}_player/{suffix}"
        self.model = MaskablePPO.load(path, env=self.env)

class RiskMetricsCallback(BaseCallback):
    def _on_step(self):
        infos = self.locals["infos"]
        for info in infos:
            if "win" in info:
                self.logger.record("game/win_rate", info["win"])
                self.logger.record("game/episode_length", info["episode_length"])
        return True

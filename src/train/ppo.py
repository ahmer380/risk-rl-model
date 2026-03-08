import torch.nn as nn

from sb3_contrib import MaskablePPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback

from src.agents.agent import RandomAgent
from src.environment.map import RiskMap
from src.train.gym_environment import RiskGymEnvironment
from src.train.rl_agent import RLAgent

'''Things that MUST be improved!
1. Training is very hidden! I have no idea what is really going on under the hood, maybe insert tensorboard? Things I would like to know are: how many Risk episodes completed
2. The training is not effective, and I don't know how this can be improved
3. The final model is around 200MB in size!
4. RiskAgent.select_action(), while only used in simulation practice, is surprisingly slow. maybe because the model is so large?
5. Quite a bit of coupling between GymRunner and RiskPPO, which makes it hard to test and iterate on either of them independently
'''

class RiskPPO:
    """Trains a PPO agent to play Risk on a given map and number of players."""
    def __init__(self, map_name: str, num_players: int):
        self.map_name = map_name
        self.num_players = num_players

        def make_env():
            agent_composition = [RLAgent(0, None)] + [RandomAgent(i) for i in range(1, num_players)]
            return RiskGymEnvironment(RiskMap.from_json(f"maps/{map_name}.json"), num_players, agent_composition)

        self.vec_env = make_vec_env(make_env, n_envs=8)

        self.policy_kwargs = dict(
            net_arch=dict(pi=[256, 256], vf=[256, 256]),
            activation_fn=nn.ReLU,
        )

        self.hyperparameters = dict(
            policy="MultiInputPolicy",
            learning_rate=3e-4,
            n_steps=4096,
            batch_size=256,
            n_epochs=4,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
        )

        self.model = MaskablePPO(
            env=self.vec_env,
            tensorboard_log=f"models/{self.map_name}_map_{self.num_players}_player/logs",
            policy_kwargs=self.policy_kwargs,
            **self.hyperparameters,
        )
    
    def train(self, total_timesteps: int):
        self.model.learn(total_timesteps=total_timesteps, progress_bar=True, callback=RiskMetricsCallback())
    
    def save(self, suffix: str):
        self.model.save(f"models/{self.map_name}_map_{self.num_players}_player/{suffix}")
    
    def load(self, suffix: str):
        self.model.load(f"models/{self.map_name}_map_{self.num_players}_player/{suffix}", env=self.vec_env)

class RiskMetricsCallback(BaseCallback):
    def _on_step(self):
        infos = self.locals["infos"]
        for info in infos:
            if "win" in info:
                self.logger.record("game/win_rate", info["win"])
                self.logger.record("game/episode_length", info["episode_length"])
        return True
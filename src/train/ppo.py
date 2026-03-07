from sb3_contrib import MaskablePPO

from src.train.gym_runner import GymRunner

class RiskPPO:
    def __init__(self, gym_runner: GymRunner):
        self.gym_runner = gym_runner

        self.hyperparameters = dict(
            policy="MultiInputPolicy",
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
        )

        self.model = MaskablePPO(
            env=self.gym_runner,
            **self.hyperparameters,
        )
    
    def train(self, total_timesteps: int):
        self.model.learn(total_timesteps=total_timesteps, progress_bar=True)
    
    def save(self, name: str):
        self.model.save(f"src/train/{name}")
    
    def load(self, name: str):
        self.model.load(f"src/train/{name}", env=self.gym_runner)
    
import unittest

import numpy as np

from src.agents.agent import RandomAgent, CommunistAgent, CapitalistAgent

from src.environment.actions import TransferMethod, DeployAction, TradeAction, BattleFromAction, BattleToAction, TransferAction, FortifyFromAction, FortifyToAction, FortifyAmountAction, SkipAction
from src.environment.map import RiskMap

from src.train.rl_agent import RLAgent
from src.train.gym_environment import RiskGymEnvironment

class TestClassicGymEnv(unittest.TestCase):
    def setUp(self):
        self.num_players = 6
        agent_composition = [RLAgent(None), CommunistAgent(), RandomAgent(), RandomAgent(), RandomAgent(), CapitalistAgent()]
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.runner = RiskGymEnvironment(self.classic_map, agent_composition)

class TestGymEnvSimulation(TestClassicGymEnv):
    def test_full_episode_run(self):
        observation, info = self.runner.reset()
        done = False

        while not done:
            mask = self.runner.action_masks()
            valid_actions = np.where(mask)[0]
            action = np.random.choice(valid_actions)
            observation, reward, terminated, truncated, info = self.runner.step(action)
            done = terminated or truncated

            self.assertTrue(self.runner.observation_space.contains(observation))
    
    def test_step_execution(self):
        observation, info = self.runner.reset()

        num_steps = 5000
        for _ in range(num_steps):
            mask = self.runner.action_masks()
            valid_actions = np.where(mask)[0]
            action = np.random.choice(valid_actions)
            observation, reward, terminated, truncated, info = self.runner.step(action)

            self.assertTrue(self.runner.observation_space.contains(observation))

            if terminated or truncated:
                self.runner.reset()

class TestGymEnvInitialisation(TestClassicGymEnv):    
    def test_max_actions(self):
        self.assertEqual(DeployAction.get_max_actions(self.classic_map), 42)
        self.assertEqual(TradeAction.get_max_actions(self.classic_map), 10)
        self.assertEqual(BattleFromAction.get_max_actions(self.classic_map), 42)
        self.assertEqual(BattleToAction.get_max_actions(self.classic_map), 42)
        self.assertEqual(TransferAction.get_max_actions(self.classic_map), 4)
        self.assertEqual(FortifyFromAction.get_max_actions(self.classic_map), 42)
        self.assertEqual(FortifyToAction.get_max_actions(self.classic_map), 42)
        self.assertEqual(FortifyAmountAction.get_max_actions(self.classic_map), 4)
        self.assertEqual(SkipAction.get_max_actions(self.classic_map), 1)
        self.assertEqual(self.runner.get_max_actions(), 229)
        self.assertEqual(self.runner.action_space.n, 229)

class TestEncodeAndDecodeActions(TestClassicGymEnv):
    def test_encode_and_decode_deploy_action(self):
        deploy_action = DeployAction(20)
        encoded = self.runner.encode_action(deploy_action)
        self.assertEqual(encoded, 20)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, deploy_action)
    
    def test_encode_and_decode_trade_action(self):
        trade_action = TradeAction([0, 3, 4])
        encoded = self.runner.encode_action(trade_action)
        self.assertEqual(encoded, 42 + 5)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, trade_action)
    
    def test_encode_and_decode_from_battle_action(self):
        battle_from_action = BattleFromAction(29)
        encoded = self.runner.encode_action(battle_from_action)
        self.assertEqual(encoded, 42 + 10 + 29)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, battle_from_action)
    
    def test_encode_and_decode_battle_to_action(self):
        battle_to_action = BattleToAction(15)
        encoded = self.runner.encode_action(battle_to_action)
        self.assertEqual(encoded, 42 + 10 + 42 + 15)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, battle_to_action)

    def test_encode_and_decode_transfer_action(self):
        transfer_action = TransferAction(TransferMethod.SPLIT)
        encoded = self.runner.encode_action(transfer_action)
        self.assertEqual(encoded, 42 + 10 + 42 + 42 + 2)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, transfer_action)
    
    def test_encode_and_decode_fortify_from_action(self):
        fortify_from_action = FortifyFromAction(3)
        encoded = self.runner.encode_action(fortify_from_action)
        self.assertEqual(encoded, 42 + 10 + 42 + 42 + 4 + 3)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, fortify_from_action)
    
    def test_encode_and_decode_fortify_to_action(self):
        fortify_to_action = FortifyToAction(31)
        encoded = self.runner.encode_action(fortify_to_action)
        self.assertEqual(encoded, 42 + 10 + 42 + 42 + 4 + 42 + 31)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, fortify_to_action)
    
    def test_encode_and_decode_fortify_amount_action(self):
        fortify_amount_action = FortifyAmountAction(TransferMethod.RANDOM)
        encoded = self.runner.encode_action(fortify_amount_action)
        self.assertEqual(encoded, 42 + 10 + 42 + 42 + 4 + 42 + 42 + 0)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, fortify_amount_action)
    
    def test_encode_and_decode_skip_action(self):
        skip_action = SkipAction()
        encoded = self.runner.encode_action(skip_action)
        self.assertEqual(encoded, self.runner.get_max_actions() - 1)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, skip_action)

if __name__ == "__main__":
    unittest.main()

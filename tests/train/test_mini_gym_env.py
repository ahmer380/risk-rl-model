import unittest

import numpy as np

import gymnasium

from src.agents.agent import CommunistAgent

from src.environment.actions import TransferMethod, DeployAction, BattleFromAction, BattleToAction, TransferAction, FortifyFromAction, FortifyToAction, FortifyAmountAction, SkipAction
from src.environment.map import RiskMap

from src.train.rl_agent import RLAgent
from src.train.gym_environment import RiskGymEnvironment

class TestMiniGymEnv(unittest.TestCase):
    def setUp(self):
        self.num_players = 2
        agent_composition = [RLAgent(None), CommunistAgent(disparity=0)]
        self.mini_map = RiskMap.from_json("maps/mini.json")
        self.runner = RiskGymEnvironment(self.mini_map, agent_composition)

class TestGymEnvSimulation(TestMiniGymEnv):
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

class TestGymEnvInitialisation(TestMiniGymEnv):    
    def test_max_actions(self):
        self.assertEqual(DeployAction.get_max_actions(self.mini_map), 8)
        self.assertEqual(BattleFromAction.get_max_actions(self.mini_map), 8)
        self.assertEqual(BattleToAction.get_max_actions(self.mini_map), 8)
        self.assertEqual(TransferAction.get_max_actions(self.mini_map), 4)
        self.assertEqual(FortifyFromAction.get_max_actions(self.mini_map), 8)
        self.assertEqual(FortifyToAction.get_max_actions(self.mini_map), 8)
        self.assertEqual(FortifyAmountAction.get_max_actions(self.mini_map), 4)
        self.assertEqual(SkipAction.get_max_actions(self.mini_map), 1)
        self.assertEqual(self.runner.get_max_actions(), 49)
        self.assertEqual(self.runner.action_space.n, 49)

    def test_observation_space(self):
        observation_space = self.runner.observation_space

        phase_space = observation_space["current_phase"]
        self.assertIsInstance(phase_space, gymnasium.spaces.MultiBinary)
        self.assertEqual(phase_space.shape, (3,))

        territories_space = observation_space["territories"]
        self.assertIsInstance(territories_space, gymnasium.spaces.Box)
        self.assertEqual(territories_space.shape, (len(self.mini_map.territories), 2))
        self.assertEqual(territories_space.dtype, np.float32)
        self.assertTrue(np.all(territories_space.low == 0.0))
        self.assertTrue(np.all(territories_space.high == 1.0))

        cards_space = observation_space["territory_card_count"]
        self.assertIsInstance(cards_space, gymnasium.spaces.Box)
        self.assertEqual(cards_space.shape, (1,))
        self.assertEqual(cards_space.dtype, np.float32)
        self.assertTrue(np.all(cards_space.low == 0.0))
        self.assertTrue(np.all(cards_space.high == 1.0))

        deploy_space = observation_space["deployment_troops"]
        self.assertIsInstance(deploy_space, gymnasium.spaces.Box)
        self.assertEqual(deploy_space.shape, (1,))
        self.assertEqual(deploy_space.dtype, np.float32)
        self.assertTrue(np.all(deploy_space.low == 0.0))
        self.assertTrue(np.all(deploy_space.high == 1.0))

        self.assertEqual(gymnasium.spaces.utils.flatdim(observation_space), 21)

    def test_initial_state_observation(self):
        self.runner.agents = [self.runner.rl_agent, CommunistAgent(disparity=0)] # rl agent is player 0
        self.runner.game_state.territory_owners = [0, 0, 0, 0, 1, 1, 1, 1]
        self.runner.game_state.territory_troops = [1, 2, 3, 4, 5, 6, 7, 8]

        observation = self.runner.encode_observation()

        np.testing.assert_array_equal(observation["current_phase"], np.array([1, 0, 0], dtype=np.int8))
        np.testing.assert_array_equal(observation["territories"], np.array(
            [[1, 0.01], [1, 0.02], [1, 0.03], [1, 0.04], [0, 0.05], [0, 0.06], [0, 0.07], [0, 0.08]],
            dtype=np.float32
        ))
        np.testing.assert_array_equal(observation["territory_card_count"], np.array([0.0], dtype=np.float32))
        np.testing.assert_array_equal(observation["deployment_troops"], np.array([0.03], dtype=np.float32))

        self.assertTrue(self.runner.observation_space.contains(observation))

class TestEncodeAndDecodeActions(TestMiniGymEnv):
    def test_encode_and_decode_deploy_action(self):
        deploy_action = DeployAction(5)
        encoded = self.runner.encode_action(deploy_action)
        self.assertEqual(encoded, 5)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, deploy_action)
    
    def test_encode_and_decode_battle_from_action(self):
        battle_from_action = BattleFromAction(2)
        encoded = self.runner.encode_action(battle_from_action)
        self.assertEqual(encoded, 8 + 2)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, battle_from_action)
    
    def test_encode_and_decode_battle_to_action(self):
        battle_to_action = BattleToAction(7)
        encoded = self.runner.encode_action(battle_to_action)
        self.assertEqual(encoded, 8 + 8 + 7)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, battle_to_action)

    def test_encode_and_decode_transfer_action(self):
        transfer_action = TransferAction(TransferMethod.ONE)
        encoded = self.runner.encode_action(transfer_action)
        self.assertEqual(encoded, 8 + 8 + 8 + 1)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, transfer_action)
    
    def test_encode_and_decode_fortify_from_action(self):
        fortify_from_action = FortifyFromAction(0)
        encoded = self.runner.encode_action(fortify_from_action)
        self.assertEqual(encoded, 8 + 8 + 8 + 4 + 0)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, fortify_from_action)
    
    def test_encode_and_decode_fortify_to_action(self):
        fortify_to_action = FortifyToAction(7)
        encoded = self.runner.encode_action(fortify_to_action)
        self.assertEqual(encoded, 8 + 8 + 8 + 4 + 8 + 7)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, fortify_to_action)
    
    def test_encode_and_decode_fortify_amount_action(self):
        fortify_amount_action = FortifyAmountAction(TransferMethod.ALL)
        encoded = self.runner.encode_action(fortify_amount_action)
        self.assertEqual(encoded, 8 + 8 + 8 + 4 + 8 + 8 + 3)
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

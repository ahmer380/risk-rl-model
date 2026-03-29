import unittest

import numpy as np

from src.agents.agent import RandomAgent, CommunistAgent

from src.environment.actions import DeployAction, TradeAction, BattleAction, TransferAction, FortifyRouteAction, FortifyAmountAction, SkipAction
from src.environment.map import RiskMap

from src.train.rl_agent import RLAgent
from src.train.gym_environment import RiskGymEnvironment

class TestGymEnvironment(unittest.TestCase):
    def setUp(self):
        self.num_players = 6
        agent_composition = [RLAgent(None), CommunistAgent(), RandomAgent(), RandomAgent(), RandomAgent(), CommunistAgent()]
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.runner = RiskGymEnvironment(self.classic_map, 6, agent_composition)

class TestGymEnvironmentSimulation(TestGymEnvironment):
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
        self.num_players = 2
        agent_composition = [RLAgent(None), RandomAgent()]
        self.classic_map = RiskMap.from_json("maps/mini.json")
        self.runner = RiskGymEnvironment(self.classic_map, 2, agent_composition)
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

class TestGymEnvironmentInitialisation(TestGymEnvironment):    
    def test_max_actions(self):
        self.assertEqual(DeployAction.get_max_actions(self.classic_map), 42)
        self.assertEqual(TradeAction.get_max_actions(self.classic_map), 10)
        self.assertEqual(BattleAction.get_max_actions(self.classic_map), 1764)
        self.assertEqual(TransferAction.get_max_actions(self.classic_map), 101)
        self.assertEqual(FortifyRouteAction.get_max_actions(self.classic_map), 1764)
        self.assertEqual(FortifyAmountAction.get_max_actions(self.classic_map), 101)
        self.assertEqual(SkipAction.get_max_actions(self.classic_map), 1)
        self.assertEqual(self.runner.get_max_actions(), 3783)
        self.assertEqual(self.runner.action_space.n, 3783)
    
    def test_initial_state_observation(self):
        observation = self.runner.encode_observation()

        np.testing.assert_array_equal(observation['active_players'], np.array([True, True, True, True, True, True]))
        np.testing.assert_equal(observation['current_player'], 0)
        np.testing.assert_equal(observation['current_phase'], 0)
        np.testing.assert_array_equal(observation['player_territory_cards'], np.array(
            [[[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]],
             [[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]],
             [[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]],
             [[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]],
             [[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]],
             [[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]]],
        ))
        np.testing.assert_equal(observation['trade_count'], 0)
        np.testing.assert_array_equal(observation['current_territory_transfer'], np.array([-1, -1]))
        np.testing.assert_array_equal(observation['current_fortify_route'], np.array([-1, -1]))
        np.testing.assert_array_equal(observation['territory_captured_this_turn'], np.array([False]))
        np.testing.assert_equal(observation['deployment_troops'], 3)

        self.assertEqual(np.shape(observation['territory_owners']), (42,))
        self.assertEqual(np.shape(observation['territory_troops']), (42,))
        self.assertTrue(all(0 <= owner < self.num_players for owner in observation['territory_owners'])) # all territories owned
        self.assertTrue(all(troops >= 1 for troops in observation['territory_troops'])) # all territories have at least 1 troop

        territories_per_player = [0] * self.num_players
        troops_per_player = [0] * self.num_players
        for territory_i in range(len(observation['territory_owners'])):
            owner = observation['territory_owners'][territory_i]
            territories_per_player[owner] += 1
            troops_per_player[owner] += observation['territory_troops'][territory_i]

        self.assertLessEqual(max(territories_per_player) - min(territories_per_player), 1) # approx equal territories
        self.assertTrue(all(troops == troops_per_player[0] for troops in troops_per_player)) # equal troops

class TestEncodeAndDecodeActions(TestGymEnvironment):
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
    
    def test_encode_and_decode_battle_action(self):
        battle_action = BattleAction(10, 15)
        encoded = self.runner.encode_action(battle_action)
        self.assertEqual(encoded, 42 + 10 + 435)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, battle_action)
    
    def test_encode_and_decode_transfer_action(self):
        transfer_action = TransferAction(50)
        encoded = self.runner.encode_action(transfer_action)
        self.assertEqual(encoded, 42 + 10 + 1764 + 50)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, transfer_action)
    
    def test_encode_and_decode_fortify_route_action(self):
        fortify_route_action = FortifyRouteAction(3, 31)
        encoded = self.runner.encode_action(fortify_route_action)
        self.assertEqual(encoded, 42 + 10 + 1764 + 101 + 157)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, fortify_route_action)
    
    def test_encode_and_decode_fortify_amount_action(self):
        fortify_amount_action = FortifyAmountAction(1)
        encoded = self.runner.encode_action(fortify_amount_action)
        self.assertEqual(encoded, 42 + 10 + 1764 + 101 + 1764 + 1)
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

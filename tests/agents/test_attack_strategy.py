import unittest

from src.agents.attack_strategy import WeightedRandomAttackStrategy, SafeBattleStrategy, TransferMethod

from src.environment.actions import ActionList, BattleAction, TransferAction, SkipAction
from src.environment.game_state import GameState
from src.environment.map import RiskMap

class TestAttackStrategy(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.game_state = GameState(self.num_players, len(self.classic_map.territories), True)

class TestWeightedRandomAttackStrategy(TestAttackStrategy):
    def test_select_action_with_full_battle_weight_returns_battle_action(self):
        strategy = WeightedRandomAttackStrategy(battle_weight=1.0)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[BattleAction(0, 1), BattleAction(2, 3)],
            transfer_actions=[TransferAction(1), TransferAction(2)],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )
        expected_actions = action_list.battle_actions

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, expected_actions)

    def test_select_action_with_zero_battle_weight_returns_transfer_or_skip(self):
        strategy = WeightedRandomAttackStrategy(battle_weight=0.0)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[BattleAction(0, 1), BattleAction(2, 3)],
            transfer_actions=[TransferAction(1), TransferAction(2), TransferAction(3)],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )
        expected_actions = action_list.transfer_actions

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, expected_actions)

    def test_select_action_without_battles_returns_skip_action(self):
        strategy = WeightedRandomAttackStrategy(battle_weight=1.0)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[SkipAction()],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, SkipAction())

class TestSafeBattleStrategy(TestAttackStrategy):
    def setUp(self):
        super().setUp()
        # Define troop counts to produce an obvious best battle: 0->10 vs 1->2 (disparity 8).
        self.game_state.territory_troops = [1] * len(self.game_state.territory_troops)
        self.game_state.territory_troops[0] = 10
        self.game_state.territory_troops[1] = 2
        self.game_state.territory_troops[2] = 6
        self.game_state.territory_troops[3] = 5

    def test_select_action_returns_best_battle_when_disparity_met(self):
        strategy = SafeBattleStrategy(disparity=5)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[BattleAction(0, 1), BattleAction(2, 3)],
            transfer_actions=[TransferAction(1), TransferAction(2), TransferAction(3)],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, BattleAction(0, 1))

    def test_select_action_with_one_transfer_method_returns_min_transfer(self):
        strategy = SafeBattleStrategy(disparity=20, transfer_method=TransferMethod.ONE)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[BattleAction(0, 1)],
            transfer_actions=[TransferAction(1), TransferAction(2), TransferAction(3)],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, TransferAction(1))

    def test_select_action_with_all_transfer_method_returns_max_transfer(self):
        strategy = SafeBattleStrategy(disparity=20, transfer_method=TransferMethod.ALL)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[BattleAction(0, 1)],
            transfer_actions=[TransferAction(1), TransferAction(2), TransferAction(3)],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, TransferAction(3))

    def test_select_action_with_split_transfer_method_returns_half_transfer(self):
        strategy = SafeBattleStrategy(disparity=20, transfer_method=TransferMethod.SPLIT)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[BattleAction(0, 1)],
            transfer_actions=[TransferAction(1), TransferAction(2), TransferAction(3), TransferAction(4)],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, TransferAction(2))

    def test_select_action_with_random_transfer_method_returns_any_transfer(self):
        strategy = SafeBattleStrategy(disparity=20, transfer_method=TransferMethod.RANDOM)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[BattleAction(0, 1)],
            transfer_actions=[TransferAction(1), TransferAction(2), TransferAction(3), TransferAction(4)],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )
        expected_actions = action_list.transfer_actions

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, expected_actions)

if __name__ == "__main__":
    unittest.main()

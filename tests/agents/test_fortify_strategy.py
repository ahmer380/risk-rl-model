import unittest

from src.agents.fortify_strategy import RandomFortifyStrategy, MinimumFortifyStrategy

from src.environment.actions import ActionList, FortifyRouteAction, FortifyAmountAction, SkipAction
from src.environment.game_state import GameState
from src.environment.map import RiskMap

class TestFortifyStrategy(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.game_state = GameState(self.num_players, len(self.classic_map.territories), True)

class TestRandomFortifyStrategy(TestFortifyStrategy):
    def test_select_action_returns_any_valid_fortify_action(self):
        strategy = RandomFortifyStrategy()
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[FortifyRouteAction(0, 1), FortifyRouteAction(2, 3)],
            fortify_amount_actions=[FortifyAmountAction(1), FortifyAmountAction(2)],
            skip_actions=[SkipAction()],
        )
        expected_actions = action_list.flatten()

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, expected_actions)

class TestMinimumFortifyStrategy(TestFortifyStrategy):
    def setUp(self):
        super().setUp()
        # Set troop counts so route 0->1 has the largest from-to difference (9 - 2 = 7).
        self.game_state.territory_troops = [1] * len(self.game_state.territory_troops)
        self.game_state.territory_troops[0] = 9
        self.game_state.territory_troops[1] = 2
        self.game_state.territory_troops[2] = 7
        self.game_state.territory_troops[3] = 5

    def test_select_action_returns_best_fortify_route_when_available(self):
        strategy = MinimumFortifyStrategy()
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[FortifyRouteAction(0, 1), FortifyRouteAction(2, 3)],
            fortify_amount_actions=[FortifyAmountAction(1), FortifyAmountAction(2), FortifyAmountAction(3)],
            skip_actions=[SkipAction()],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, FortifyRouteAction(0, 1))

    def test_select_action_returns_split_fortify_amount_when_no_routes(self):
        strategy = MinimumFortifyStrategy()
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[FortifyAmountAction(1), FortifyAmountAction(2), FortifyAmountAction(3), FortifyAmountAction(4)],
            skip_actions=[SkipAction()],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, FortifyAmountAction(2))

    def test_select_action_returns_skip_when_only_skip_is_available(self):
        strategy = MinimumFortifyStrategy()
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

if __name__ == "__main__":
    unittest.main()

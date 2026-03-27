import unittest

from src.agents.fortify_strategy import RandomFortifyStrategy, MinimumFortifyStrategy, MaximumFortifyStrategy

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
            fortify_amount_actions=[],
            skip_actions=[],
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
            fortify_route_actions=[FortifyRouteAction(0, 1), FortifyRouteAction(2, 3), FortifyRouteAction(1, 3)],
            fortify_amount_actions=[],
            skip_actions=[],
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
            skip_actions=[],
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

class TestMaximumFortifyStrategy(TestFortifyStrategy):
    def setUp(self):
        super().setUp()
        self.game_state.current_player = 0
        self.game_state.territory_owners = [1] * len(self.game_state.territory_owners)
        for territory_id in [0, 1, 2, 3, 4]:
            self.game_state.territory_owners[territory_id] = 0

        self.game_state.territory_troops = [1] * len(self.game_state.territory_troops)
        self.game_state.territory_troops[0] = 9
        self.game_state.territory_troops[1] = 7
        self.game_state.territory_troops[2] = 7
        self.game_state.territory_troops[3] = 6
        self.game_state.territory_troops[4] = 3

    def test_select_action_prioritises_fortifying_towards_capitals_from_non_capitals(self):
        strategy = MaximumFortifyStrategy(capitals=2)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[FortifyRouteAction(3, 1), FortifyRouteAction(3, 4), FortifyRouteAction(4, 2)],
            fortify_amount_actions=[],
            skip_actions=[],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, FortifyRouteAction(3, 1))

    def test_select_action_ignores_routes_originating_from_capitals(self):
        strategy = MaximumFortifyStrategy(capitals=2)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[FortifyRouteAction(0, 4), FortifyRouteAction(1, 4), FortifyRouteAction(3, 4)],
            fortify_amount_actions=[],
            skip_actions=[],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, FortifyRouteAction(3, 4))

    def test_select_action_returns_max_amount_when_no_valid_routes(self):
        strategy = MaximumFortifyStrategy(capitals=2)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[FortifyAmountAction(1), FortifyAmountAction(3), FortifyAmountAction(5)],
            skip_actions=[],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, FortifyAmountAction(5))

    def test_select_action_returns_skip_when_only_skip_is_available(self):
        strategy = MaximumFortifyStrategy(capitals=2)
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

    def test_get_capital_territory_ids_includes_tie_at_threshold(self):
        strategy = MaximumFortifyStrategy(capitals=2)
        capital_territory_ids = strategy.get_capital_territory_ids(self.game_state)

        self.assertCountEqual(capital_territory_ids, [0, 1, 2])

if __name__ == "__main__":
    unittest.main()

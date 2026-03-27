import unittest

from src.agents.draft_strategy import RandomDraftStrategy, MinimumDeployStrategy, MaximumDeployStrategy, ContinentalDeployStrategy

from src.environment.actions import ActionList, DeployAction, TradeAction, SkipAction
from src.environment.game_state import GameState
from src.environment.map import RiskMap

class TestDraftStrategy(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.game_state = GameState(self.num_players, len(self.classic_map.territories), True)

class TestRandomDraftStrategy(TestDraftStrategy):
    def test_select_action_returns_any_valid_draft_action(self):
        strategy = RandomDraftStrategy()
        action_list = ActionList(
            deploy_actions=[DeployAction(0), DeployAction(1)],
            trade_actions=[TradeAction([0, 1, 2])],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[SkipAction()],
        )
        expected_actions = action_list.flatten()

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, expected_actions)

class TestMinimumDeployStrategy(TestDraftStrategy):
    def setUp(self):
        super().setUp()
        # Force player 0 ownership on territory IDs 0,1,2 only (Alaska, Alberta, Central America).
        self.game_state.territory_owners = [1] * len(self.game_state.territory_owners)
        self.game_state.territory_owners[0] = 0
        self.game_state.territory_owners[1] = 0
        self.game_state.territory_owners[2] = 0
        # Set troop counts on those territories so ID 1 is the unique minimum: 0->5, 1->2, 2->4.
        self.game_state.territory_troops = [1] * len(self.game_state.territory_troops)
        self.game_state.territory_troops[0] = 5
        self.game_state.territory_troops[1] = 2
        self.game_state.territory_troops[2] = 4

    def test_select_action_returns_lowest_troop_deploy(self):
        strategy = MinimumDeployStrategy()
        action_list = ActionList(
            deploy_actions=[DeployAction(0), DeployAction(1), DeployAction(2)],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertEqual(selected_action, DeployAction(1))

    def test_select_action_without_deploy_returns_trade_or_skip(self):
        strategy = MinimumDeployStrategy()
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[TradeAction([0, 1, 2])],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[SkipAction()],
        )
        expected_actions = action_list.trade_actions + action_list.skip_actions

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, expected_actions)


class TestMaximumDeployStrategy(TestDraftStrategy):
    def setUp(self):
        super().setUp()
        # Player 0 owns IDs 0-3 (Alaska, Alberta, Central America, Eastern United States).
        self.game_state.territory_owners = [1] * len(self.game_state.territory_owners)
        self.game_state.territory_owners[0] = 0
        self.game_state.territory_owners[1] = 0
        self.game_state.territory_owners[2] = 0
        self.game_state.territory_owners[3] = 0

        # Troop profile creates top-2 threshold with a tie: 0->8, 1->7, 2->7, 3->3.
        self.game_state.territory_troops = [1] * len(self.game_state.territory_troops)
        self.game_state.territory_troops[0] = 8
        self.game_state.territory_troops[1] = 3
        self.game_state.territory_troops[2] = 7
        self.game_state.territory_troops[3] = 7

    def test_select_action_returns_one_of_top_capital_deploys(self):
        strategy = MaximumDeployStrategy(capitals=2)
        action_list = ActionList(
            deploy_actions=[DeployAction(0), DeployAction(1), DeployAction(2), DeployAction(3)],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )

        expected_actions = set([DeployAction(0).__repr__(), DeployAction(2).__repr__(), DeployAction(3).__repr__()])
        selected_actions = set()
        for _ in range(50):
            selected_actions.add(strategy.select_action(action_list, self.game_state, self.classic_map).__repr__())
        self.assertEqual(expected_actions, selected_actions)

    def test_select_action_without_deploy_returns_trade_or_skip(self):
        strategy = MaximumDeployStrategy(capitals=2)
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[TradeAction([0, 1, 2])],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[SkipAction()],
        )
        expected_actions = action_list.trade_actions + action_list.skip_actions

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, expected_actions)


class TestContinentalDeployStrategy(TestDraftStrategy):
    def setUp(self):
        super().setUp()
        self.south_america_territory_ids = [9, 10, 11, 12]
        self.asia_except_siam_territory_ids = [26, 27, 28, 29, 30, 31, 32, 33, 35, 36, 37]
        self.game_state.territory_owners = [1] * len(self.game_state.territory_owners)

        # Player 0 fully controls South America, and controls all of Asia except Siam (ID 34).
        for territory_id in self.south_america_territory_ids:
            self.game_state.territory_owners[territory_id] = 0
        for territory_id in self.asia_except_siam_territory_ids:
            self.game_state.territory_owners[territory_id] = 0

    def test_select_action_returns_deploy_in_most_controlled_continent(self):
        strategy = ContinentalDeployStrategy()

        south_america_actions = [
            DeployAction(territory_id)
            for territory_id in self.south_america_territory_ids
        ]
        asia_action = DeployAction(self.asia_except_siam_territory_ids[0])

        action_list = ActionList(
            deploy_actions=south_america_actions + [asia_action],
            trade_actions=[],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[],
        )
        expected_actions = south_america_actions

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, expected_actions)

    def test_select_action_without_deploy_returns_trade_or_skip(self):
        strategy = ContinentalDeployStrategy()
        action_list = ActionList(
            deploy_actions=[],
            trade_actions=[TradeAction([0, 1, 2])],
            battle_actions=[],
            transfer_actions=[],
            fortify_route_actions=[],
            fortify_amount_actions=[],
            skip_actions=[SkipAction()],
        )
        expected_actions = action_list.trade_actions + action_list.skip_actions

        for _ in range(50):
            selected_action = strategy.select_action(action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, expected_actions)

if __name__ == "__main__":
    unittest.main()

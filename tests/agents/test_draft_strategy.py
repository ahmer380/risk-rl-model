import unittest

from src.agents.draft_strategy import RandomDraftStrategy, MinimumDraftStrategy, MaximumDraftStrategy, ContinentalDraftStrategy

from src.environment.actions import DeployAction
from src.environment.environment import RiskEnvironment
from src.environment.map import RiskMap

class TestDraftStrategy(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.environment = RiskEnvironment(self.classic_map, self.num_players)
        self.game_state = self.environment.current_state

        # Shared baseline scenario used across strategy test modules.
        self.game_state.territory_owners = [1] * len(self.game_state.territory_owners)

        # Set player 0 to own South American territories
        self.game_state.territory_owners[9], self.game_state.territory_troops[9] = 0, 4
        self.game_state.territory_owners[10], self.game_state.territory_troops[10] = 0, 8
        self.game_state.territory_owners[11], self.game_state.territory_troops[11] = 0, 3
        self.game_state.territory_owners[12], self.game_state.territory_troops[12] = 0, 2

        # Set player 0 to own some Asian territories except Siam
        self.game_state.territory_owners[26], self.game_state.territory_troops[26] = 0, 8
        self.game_state.territory_owners[27], self.game_state.territory_troops[27] = 0, 10
        self.game_state.territory_owners[28], self.game_state.territory_troops[28] = 0, 4
        self.game_state.territory_owners[29], self.game_state.territory_troops[29] = 0, 7
        self.game_state.territory_owners[30], self.game_state.territory_troops[30] = 0, 5
        self.game_state.territory_owners[31], self.game_state.territory_troops[31] = 0, 3
        self.game_state.territory_owners[32], self.game_state.territory_troops[32] = 0, 2
        self.game_state.territory_owners[33], self.game_state.territory_troops[33] = 0, 4
        self.game_state.territory_owners[35], self.game_state.territory_troops[35] = 0, 1
        self.game_state.territory_owners[36], self.game_state.territory_troops[36] = 0, 5
        self.game_state.territory_owners[37], self.game_state.territory_troops[37] = 0, 8

        self.deployment_troops = 1
        self.action_list = self.environment.get_action_list()

class TestRandomDraftStrategy(TestDraftStrategy):
    def setUp(self):
        super().setUp()
        self.draft_strategy = RandomDraftStrategy()

    def test_select_action_returns_any_valid_deploy_action(self):
        for _ in range(50):
            selected_action = self.draft_strategy.select_action(self.action_list, self.game_state, self.classic_map)
            self.assertIn(selected_action, self.action_list.deploy_actions)

class TestMinimumDraftStrategy(TestDraftStrategy):
    def setUp(self):
        super().setUp()
        self.draft_strategy = MinimumDraftStrategy()

    def test_select_action_returns_lowest_troop_deploy(self):
        selected_action = self.draft_strategy.select_action(self.action_list, self.game_state, self.classic_map)

        self.assertEqual(selected_action, DeployAction(35))

class TestMaximumDraftStrategy(TestDraftStrategy):
    def setUp(self):
        super().setUp()
        self.draft_strategy = MaximumDraftStrategy(capitals=2)

    def test_select_action_returns_one_of_top_capital_deploys(self):
        expected_actions = {DeployAction(10).__repr__(),DeployAction(26).__repr__(), DeployAction(27).__repr__(), DeployAction(37).__repr__()}
        selected_actions = set()
        for _ in range(50):
            selected_actions.add(self.draft_strategy.select_action(self.action_list, self.game_state, self.classic_map).__repr__())

        self.assertEqual(expected_actions, selected_actions)

class TestContinentalDraftStrategy(TestDraftStrategy):
    def setUp(self):
        super().setUp()
        self.draft_strategy = ContinentalDraftStrategy()

    def test_select_action_returns_deploy_in_most_controlled_continent(self):
        expected_actions = {DeployAction(9).__repr__(), DeployAction(10).__repr__(), DeployAction(11).__repr__(), DeployAction(12).__repr__()}
        selected_actions = set()
        for _ in range(50):
            selected_actions.add(self.draft_strategy.select_action(self.action_list, self.game_state, self.classic_map).__repr__())

        self.assertEqual(expected_actions, selected_actions)

if __name__ == "__main__":
    unittest.main()

import unittest

from src.agents.fortify_strategy import RandomFortifyStrategy, MinimumFortifyStrategy, MaximumFortifyStrategy

from src.environment.actions import FortifyRouteAction, FortifyAmountAction, SkipAction

from src.environment.environment import RiskEnvironment
from src.environment.game_state import GamePhase
from src.environment.map import RiskMap

class TestFortifyStrategy(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.environment = RiskEnvironment(self.classic_map, self.num_players)
        self.game_state = self.environment.current_state

        self.game_state.current_phase = GamePhase.FORTIFY
        self.game_state.deployment_troops = 0
        self.game_state.current_territory_transfer = (-1, -1)
        self.game_state.current_fortify_route = (-1, -1)

        self.game_state.territory_owners = [1] * len(self.game_state.territory_owners)
        self.game_state.territory_troops = [1] * len(self.game_state.territory_troops)

        # Assign ownership to Congo, East Africa, and South Africa, territories that are all connected to one-another
        self.game_state.territory_owners[20], self.game_state.territory_troops[20] = 0, 2
        self.game_state.territory_owners[21], self.game_state.territory_troops[21] = 0, 7
        self.game_state.territory_owners[25], self.game_state.territory_troops[25] = 0, 10

        self.action_list = self.environment.get_action_list()

class TestRandomFortifyStrategy(TestFortifyStrategy):
    def setUp(self):
        super().setUp()
        self.fortify_strategy = RandomFortifyStrategy()

    def test_select_action_returns_any_valid_fortify_route_action(self):
        expected_actions = {
            FortifyRouteAction(20, 21).__repr__(),
            FortifyRouteAction(20, 25).__repr__(),
            FortifyRouteAction(21, 20).__repr__(),
            FortifyRouteAction(21, 25).__repr__(),
            FortifyRouteAction(25, 20).__repr__(),
            FortifyRouteAction(25, 21).__repr__(),
            SkipAction().__repr__()
        }
        selected_actions = set()
        for _ in range(50):
            selected_actions.add(self.fortify_strategy.select_action(self.action_list, self.game_state, self.classic_map).__repr__())

        self.assertEqual(expected_actions, selected_actions)

class TestMinimumFortifyStrategy(TestFortifyStrategy):
    def setUp(self):
        super().setUp()
        self.fortify_strategy = MinimumFortifyStrategy()

    def test_strategy_splits_half_troops_between_most_and_least_populous_territories(self):
        selected_fortify_route_action = self.fortify_strategy.select_action(self.action_list, self.game_state, self.classic_map)
        self.assertEqual(selected_fortify_route_action, FortifyRouteAction(25, 20))
        self.environment.step(selected_fortify_route_action)
        self.action_list = self.environment.get_action_list()

        selected_fortify_amount_action = self.fortify_strategy.select_action(self.action_list, self.game_state, self.classic_map)
        self.assertEqual(selected_fortify_amount_action, FortifyAmountAction(4))
    
class TestMaximumFortifyStrategy(TestFortifyStrategy):
    def setUp(self):
        super().setUp()
        self.fortify_strategy = MaximumFortifyStrategy(capitals=1)

    def test_strategy_moves_all_troops_to_most_populous_territory(self):
        selected_fortify_route_action = self.fortify_strategy.select_action(self.action_list, self.game_state, self.classic_map)
        self.assertEqual(selected_fortify_route_action, FortifyRouteAction(21, 25))
        self.environment.step(selected_fortify_route_action)
        self.action_list = self.environment.get_action_list()

        selected_fortify_amount_action = self.fortify_strategy.select_action(self.action_list, self.game_state, self.classic_map)
        self.assertEqual(selected_fortify_amount_action, FortifyAmountAction(6))

if __name__ == "__main__":
    unittest.main()

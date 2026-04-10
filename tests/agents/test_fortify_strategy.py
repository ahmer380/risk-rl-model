import unittest

from src.agents.fortify_strategy import RandomFortifyStrategy, MinimumFortifyStrategy, MaximumFortifyStrategy

from src.environment.actions import FortifyFromAction, FortifyToAction, FortifyAmountAction, SkipAction, MAX_TROOP_TRANSFER

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
        self.game_state.current_fortify = (-1, -1)

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
        self.game_state.territory_troops = [2] * len(self.game_state.territory_troops)

    def test_select_action_returns_any_valid_fortify_route_action(self):
        expected_fortify_actions = {
            (FortifyFromAction(20), FortifyToAction(21), FortifyAmountAction(1)).__repr__(),
            (FortifyFromAction(20), FortifyToAction(25), FortifyAmountAction(1)).__repr__(),
            (FortifyFromAction(21), FortifyToAction(20), FortifyAmountAction(1)).__repr__(),
            (FortifyFromAction(21), FortifyToAction(25), FortifyAmountAction(1)).__repr__(),
            (FortifyFromAction(25), FortifyToAction(20), FortifyAmountAction(1)).__repr__(),
            (FortifyFromAction(25), FortifyToAction(21), FortifyAmountAction(1)).__repr__()
        }
        selected_actions = set()
        for _ in range(50):
            selected_actions.add(self.fortify_strategy.compute_best_fortify(self.action_list, self.game_state, self.classic_map).__repr__())

        self.assertEqual(expected_fortify_actions, selected_actions)

class TestMinimumFortifyStrategy(TestFortifyStrategy):
    def setUp(self):
        super().setUp()
        self.fortify_strategy = MinimumFortifyStrategy()

    def test_strategy_splits_half_troops_between_most_and_least_populous_territories(self):
        expected_fortify_action = (FortifyFromAction(25), FortifyToAction(20), FortifyAmountAction(4))

        self.assertEqual(self.fortify_strategy.compute_best_fortify(self.action_list, self.game_state, self.classic_map).__repr__(), expected_fortify_action.__repr__())
    
class TestMaximumFortifyStrategy(TestFortifyStrategy):
    def setUp(self):
        super().setUp()
        self.fortify_strategy = MaximumFortifyStrategy(capitals=1)

    def test_strategy_moves_all_troops_from_capital_to_non_capital(self):
        expected_fortify_actions = {
            (FortifyFromAction(25), FortifyToAction(20), FortifyAmountAction(MAX_TROOP_TRANSFER)).__repr__(),
            (FortifyFromAction(25), FortifyToAction(21), FortifyAmountAction(MAX_TROOP_TRANSFER)).__repr__(),
        }

        selected_actions = set()
        for _ in range(50):
            selected_actions.add(self.fortify_strategy.compute_best_fortify(self.action_list, self.game_state, self.classic_map).__repr__())

        self.assertEqual(expected_fortify_actions, selected_actions)

if __name__ == "__main__":
    unittest.main()

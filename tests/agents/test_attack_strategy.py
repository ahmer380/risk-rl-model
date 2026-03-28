import unittest

from src.agents.attack_strategy import WeightedRandomAttackStrategy, SafeBattleStrategy, TransferMethod

from src.environment.actions import BattleAction, TransferAction, SkipAction
from src.environment.environment import RiskEnvironment
from src.environment.game_state import GamePhase
from src.environment.map import RiskMap

class TestAttackStrategy(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.environment = RiskEnvironment(self.classic_map, self.num_players)
        self.game_state = self.environment.current_state

        self.game_state.current_phase = GamePhase.ATTACK
        self.game_state.deployment_troops = 0
        self.game_state.current_territory_transfer = (-1, -1)
        self.game_state.current_fortify_route = (-1, -1)

        self.game_state.territory_owners = [1] * len(self.game_state.territory_owners)
        self.game_state.territory_troops = [1] * len(self.game_state.territory_troops)
        self.game_state.territory_troops[20] = 6
        self.game_state.territory_troops[23] = 2

        self.game_state.territory_owners[25] = 0 # South Africa
        self.game_state.territory_troops[25] = 4

        self.action_list = self.environment.get_action_list()

class TestWeightedRandomAttackStrategy(TestAttackStrategy):
    def setUp(self):
        super().setUp()
        self.attack_strategy = WeightedRandomAttackStrategy(battle_weight=1.0)

    def test_select_action_with_full_battle_weight_returns_battle_action(self):
        expected_actions = {BattleAction(25, 20).__repr__(), BattleAction(25, 21).__repr__(), BattleAction(25, 23).__repr__()}
        selected_actions = set()
        for _ in range(50):
            selected_actions.add(self.attack_strategy.select_action(self.action_list, self.game_state, self.classic_map).__repr__())

        self.assertEqual(expected_actions, selected_actions)
    
    def test_select_action_with_half_battle_weight_returns_battle_and_skip_action(self):
        self.attack_strategy = WeightedRandomAttackStrategy(battle_weight=0.5)
        expected_actions = {BattleAction(25, 20).__repr__(), BattleAction(25, 21).__repr__(), BattleAction(25, 23).__repr__(), SkipAction().__repr__()}
        selected_actions = set()
        for _ in range(50):
            selected_actions.add(self.attack_strategy.select_action(self.action_list, self.game_state, self.classic_map).__repr__())

        self.assertEqual(expected_actions, selected_actions)
    
    def test_select_action_with_zero_battle_weight_returns_skip_action(self):
        self.attack_strategy = WeightedRandomAttackStrategy(battle_weight=0.0)
        selected_action = self.attack_strategy.select_action(self.action_list, self.game_state, self.classic_map)
        
        self.assertEqual(selected_action, SkipAction())

class TestSafeBattleStrategy(TestAttackStrategy):
    def setUp(self):
        super().setUp()

        self.attack_strategy = SafeBattleStrategy(disparity=3)

    def test_select_action_returns_best_battle_when_disparity_met(self):
        selected_action = self.attack_strategy.select_action(self.action_list, self.game_state, self.classic_map)
        
        self.assertEqual(selected_action, BattleAction(25, 21))
    
    def test_select_action_returns_skip_when_disparity_not_met(self):
        self.attack_strategy = SafeBattleStrategy(disparity=4)
        selected_action = self.attack_strategy.select_action(self.action_list, self.game_state, self.classic_map)
        
        self.assertEqual(selected_action, SkipAction())

class TestTransferMethod(TestAttackStrategy):
    def setUp(self):
        super().setUp()

        self.game_state.territory_troops[20] = 0
        self.game_state.current_territory_transfer = (25, 20)
        self.action_list = self.environment.get_action_list()
        self.attack_strategy = SafeBattleStrategy(disparity=3)

    def test_select_non_battle_action_random(self):
        self.attack_strategy.transfer_method = TransferMethod.RANDOM

        expected_actions = {TransferAction(1).__repr__(), TransferAction(2).__repr__(), TransferAction(3).__repr__()}
        selected_actions = set()
        for _ in range(50):
            selected_actions.add(self.attack_strategy.select_action(self.action_list, self.game_state, self.classic_map).__repr__())

        self.assertEqual(expected_actions, selected_actions)

    def test_select_non_battle_action_one(self):
        self.attack_strategy.transfer_method = TransferMethod.ONE

        selected_action = self.attack_strategy.select_action(self.action_list, self.game_state, self.classic_map)
        self.assertEqual(selected_action, TransferAction(1))

    def test_select_non_battle_action_all(self):
        self.attack_strategy.transfer_method = TransferMethod.ALL
        selected_action = self.attack_strategy.select_action(self.action_list, self.game_state, self.classic_map)

        self.assertEqual(selected_action, TransferAction(3))

    def test_select_non_battle_action_split(self):
        self.attack_strategy.transfer_method = TransferMethod.SPLIT
        selected_action = self.attack_strategy.select_action(self.action_list, self.game_state, self.classic_map)

        self.assertEqual(selected_action, TransferAction(2))

if __name__ == "__main__":
    unittest.main()

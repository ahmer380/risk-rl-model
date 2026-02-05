import unittest

from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap
from src.environment.actions import Action, DeployAction, TradeAction, BattleAction, TransferAction, FortifyAction, SkipAction

class TestAction(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.game_state = GameState(self.num_players, len(self.classic_map.territories), True)

class TestDeployAction(TestAction):
    def test_get_deploy_action_list_for_initial_state(self):
        player_owned_territory_ids = self.game_state.get_player_owned_territory_ids()
        self.assertEqual(len(player_owned_territory_ids), 11)
        self.assertEqual(self.game_state.deployment_troops, 3)

        actions = DeployAction.get_action_list(self.game_state)
        self.assertEqual(len(actions), 286) # Using the Stars and Bars formula: C(n+k-1, k-1) = C(3+11-1, 11-1) = C(13, 10) = 286
        
        deployments_set = set()
        for action in actions:
            self.assertNotIn(tuple(sorted(action.deployments)), deployments_set) # ensure no duplicate actions
            deployments_set.add(tuple(sorted(action.deployments)))

            for deployment in action.deployments:
                self.assertIn(deployment[0], player_owned_territory_ids) # only deploy to owned territories
                self.assertGreater(deployment[1], 0) # positive troop count

            self.assertEqual(sum(deployment[1] for deployment in action.deployments), 3) # total deployment must equal available troops
    
    def test_get_deploy_action_list_for_non_draft_phase(self):
        self.game_state.current_phase = GamePhase.ATTACK
        actions = DeployAction.get_action_list(self.game_state)
        self.assertEqual(len(actions), 0)
    
    def test_apply_deploy_action(self):
        action = DeployAction([(0, 1), (1, 2)]) # Deploy 1 troop to territory 0 and 2 troops to territory 1
        new_state = action.apply(self.game_state)

        self.assertEqual(new_state.territory_troops[0], self.game_state.territory_troops[0] + 1)
        self.assertEqual(new_state.territory_troops[1], self.game_state.territory_troops[1] + 2)
        for i in range(2, len(self.game_state.territory_troops)):
            self.assertEqual(new_state.territory_troops[i], self.game_state.territory_troops[i]) # other territories should be unchanged

class TestTradeAction(TestAction):
    pass

class TestBattleAction(TestAction):
    pass

class TestTransferAction(TestAction):
    pass

class TestFortifyAction(TestAction):
    pass

class TestSkipAction(TestAction):
    pass

if __name__ == "__main__":
    unittest.main()

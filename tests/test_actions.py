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
        
        self.assertEqual(new_state.deployment_troops, 0)

class TestTradeAction(TestAction):
    pass

class TestBattleAction(TestAction):
    pass

class TestTransferAction(TestAction):
    pass

class TestFortifyAction(TestAction):
    pass

class TestSkipAction(TestAction):
    def test_get_skip_action_list_for_initial_state(self):
        actions = SkipAction.get_action_list(self.game_state)
        self.assertEqual(len(actions), 0) # Skip action should not be available if there are troops to deploy during the draft phase
    
    def test_get_skip_action_list_after_troops_deployed(self):
        actions = SkipAction.get_action_list(DeployAction([(0, 3)]).apply(self.game_state))
        self.assertEqual(len(actions), 1)
    
    def test_apply_skip_action(self):
        attack_phase_state = SkipAction().apply(DeployAction([(0, 3)]).apply(self.game_state))
        self.assertEqual(attack_phase_state.current_phase, GamePhase.ATTACK)
        self.assertEqual(attack_phase_state.current_player, 0)

        fortify_phase_state = SkipAction().apply(attack_phase_state)
        self.assertEqual(fortify_phase_state.current_phase, GamePhase.FORTIFY)
        self.assertEqual(fortify_phase_state.current_player, 0)

        next_player_state = SkipAction().apply(fortify_phase_state)
        self.assertEqual(next_player_state.current_phase, GamePhase.DRAFT)
        self.assertEqual(next_player_state.current_player, 1)
        # Assertion for next_player_state.deployment_troops is not checked since RiskEnvironment injects this property

if __name__ == "__main__":
    unittest.main()

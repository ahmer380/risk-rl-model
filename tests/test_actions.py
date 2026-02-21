import unittest

from src.environment.game_state import GameState, GamePhase, CombatArm, TerritoryCard
from src.environment.map import RiskMap
from src.environment.actions import DeployAction, TradeAction, BattleAction, TransferAction, FortifyRouteAction, FortifyAmountAction, SkipAction

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

        actions = DeployAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 11)
        
        deployments_set = set()
        for action in actions:
            self.assertIn(action.territory_id, player_owned_territory_ids)
            self.assertNotIn(action.territory_id, deployments_set) # ensure no duplicate actions
            deployments_set.add(action.territory_id)
    
    def test_get_deploy_action_list_for_non_draft_phase(self):
        self.game_state.current_phase = GamePhase.ATTACK
        actions = DeployAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_apply_deploy_action(self):
        action = DeployAction(0)
        new_state = action.apply(self.game_state, self.classic_map)

        self.assertEqual(new_state.territory_troops[0], self.game_state.territory_troops[0] + 1)
        for i in range(1, len(self.game_state.territory_troops)):
            self.assertEqual(new_state.territory_troops[i], self.game_state.territory_troops[i]) # other territories should remain unchanged
        
        self.assertEqual(new_state.deployment_troops, 2)

class TestTradeAction(TestAction):
    def test_get_trade_action_list_for_initial_state(self):
        actions = TradeAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_get_trade_action_list_with_cards(self):
        tc = self.game_state.player_territory_cards[0] = [
            TerritoryCard(CombatArm.INFANTRY, 3),
            TerritoryCard(CombatArm.CAVALRY, 1),
            TerritoryCard(CombatArm.INFANTRY, 2),
            TerritoryCard(CombatArm.WILD, 0),
        ]

        actions = TradeAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 3) 
        self.assertTrue(any(action.territory_cards == [tc[3], tc[1], tc[0]] for action in actions)) # 3 different cards
        self.assertTrue(any(action.territory_cards == [tc[3], tc[1], tc[2]] for action in actions)) # 3 different cards
        self.assertTrue(any(action.territory_cards == [tc[3], tc[2], tc[0]] for action in actions)) # 3 cards of the same type
    
    def test_get_trade_action_list_for_non_draft_phase(self):
        self.game_state.current_phase = GamePhase.ATTACK
        actions = TradeAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_apply_trade_action(self):
        tc = self.game_state.player_territory_cards[0] = [
            TerritoryCard(CombatArm.INFANTRY, 3),
            TerritoryCard(CombatArm.CAVALRY, 1),
            TerritoryCard(CombatArm.INFANTRY, 2),
            TerritoryCard(CombatArm.WILD, 0),
        ]
        action = TradeAction([tc[0], tc[1], tc[2]])
        new_state = action.apply(self.game_state, self.classic_map)

        self.assertEqual(len(new_state.player_territory_cards[0]), 1) # 3 cards should be removed
        self.assertIn(tc[3], new_state.player_territory_cards[0])
        self.assertEqual(new_state.deployment_troops, self.game_state.deployment_troops + 4) # First trade-in should give 4 troops 

class TestBattleAction(TestAction):
    def setUp(self):
        super().setUp()

        # Statically define territory ownership and troop counts to ensure consistent test results
        self.game_state.current_phase = GamePhase.ATTACK
        self.game_state.territory_owners = [1] * len(self.game_state.territory_owners)
        self.game_state.territory_owners[0], self.game_state.territory_owners[1], self.game_state.territory_owners[2] = 0, 0, 0 # Player 0 owns Alaska, Alberta, and Central America
        self.game_state.territory_troops = [5] * len(self.game_state.territory_troops) 
        self.game_state.territory_troops[2] = 1 # Central America only has 1 troop, so it cannot be an attacker

        self.game_state.player_territory_cards[1] = [TerritoryCard(CombatArm.WILD, 5)]
        self.game_state.player_territory_cards[3] = [TerritoryCard(CombatArm.INFANTRY, 2)]
    
    def test_get_battle_action_list(self):
        actions = BattleAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 5)
        self.assertTrue(any(self.classic_map.territories[action.attacker_territory_id].name == "Alaska" and self.classic_map.territories[action.defender_territory_id].name == "Kamchatka" for action in actions))
        self.assertTrue(any(self.classic_map.territories[action.attacker_territory_id].name == "Alaska" and self.classic_map.territories[action.defender_territory_id].name == "Northwest Territory" for action in actions))
        self.assertTrue(any(self.classic_map.territories[action.attacker_territory_id].name == "Alberta" and self.classic_map.territories[action.defender_territory_id].name == "Northwest Territory" for action in actions))
        self.assertTrue(any(self.classic_map.territories[action.attacker_territory_id].name == "Alberta" and self.classic_map.territories[action.defender_territory_id].name == "Ontario" for action in actions))
        self.assertTrue(any(self.classic_map.territories[action.attacker_territory_id].name == "Alberta" and self.classic_map.territories[action.defender_territory_id].name == "Western United States" for action in actions))
    
    def test_get_battle_action_list_for_non_attack_phase(self):
        self.game_state.current_phase = GamePhase.FORTIFY
        actions = BattleAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_get_battle_action_list_during_current_territory_transfer(self):
        self.game_state.current_territory_transfer = (0, 5) 
        actions = BattleAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0) # Cannot initiate another attack while a territory transfer is still pending resolution
    
    def test_apply_battle_action_loss(self):
        self.game_state.territory_troops[0] = 2
        self.game_state.territory_troops[5] = 10
        action = BattleAction(0, 5) # Attack from Alaska to Kamchatka, where P(Win) = 0
        new_state = action.apply(self.game_state, self.classic_map)
        
        self.assertEqual(new_state.territory_troops[0], 1) # Attacker should lose all but 1 troop
        self.assertEqual(new_state.territory_owners[5], 1) 
        self.assertLessEqual(new_state.territory_troops[5], 10)
        self.assertEqual(new_state.current_territory_transfer, (-1, -1))
        self.assertEqual(new_state.territory_captured_this_turn, False)
    
    def test_apply_battle_action_win_but_no_elimination(self):
        self.game_state.territory_troops[0] = 10
        self.game_state.territory_troops[5] = 1
        action = BattleAction(0, 5) # Attack from Alaska to Kamchatka, where P(Win) = 1
        new_state = action.apply(self.game_state, self.classic_map)

        self.assertGreaterEqual(new_state.territory_troops[0], 2)
        self.assertEqual(new_state.territory_troops[5], 0)
        self.assertEqual(new_state.current_territory_transfer, (0, 5))
        self.assertEqual(new_state.territory_captured_this_turn, True)
        self.assertEqual(new_state.active_players[1], True) # Defender should still be active since they own other territories
        self.assertEqual(len(new_state.player_territory_cards[1]), 1)
        self.assertEqual(len(new_state.player_territory_cards[0]), 0)
    
    def test_apply_battle_action_win_and_elimination(self):
        self.game_state.territory_owners[5] = 3 # Only difference is that we make the defender be player 3, who only owns this territory
        self.game_state.territory_troops[0] = 10
        self.game_state.territory_troops[5] = 1
        action = BattleAction(0, 5) # Attack from Alaska to Kamchatka, where P(Win) = 1
        new_state = action.apply(self.game_state, self.classic_map)

        self.assertGreaterEqual(new_state.territory_troops[0], 2)
        self.assertEqual(new_state.territory_troops[5], 0)
        self.assertEqual(new_state.current_territory_transfer, (0, 5))
        self.assertEqual(new_state.territory_captured_this_turn, True)
        self.assertEqual(new_state.active_players[3], False) # Defender should be eliminated since they own no other territories
        self.assertEqual(len(new_state.player_territory_cards[3]), 0)
        self.assertEqual(len(new_state.player_territory_cards[0]), 1) 

class TestTransferAction(TestAction):
    def setUp(self):
        super().setUp()

        self.game_state.current_phase = GamePhase.ATTACK
        self.game_state.current_territory_transfer = (0, 5)
        self.game_state.territory_owners[0] = 0
        self.game_state.territory_troops[0] = 7
        self.game_state.territory_owners[5] = 0
        self.game_state.territory_troops[5] = 0
    
    def test_get_transfer_action_list(self):
        actions = TransferAction.get_action_list(self.game_state, self.classic_map)
        
        self.assertEqual(len(actions), 6)
        for i, action in enumerate(actions):
            self.assertEqual(action.troop_count, i + 1)
    
    def test_get_transfer_action_list_while_no_territory_transfer_pending(self):
        self.game_state.current_territory_transfer = (-1, -1)
        actions = TransferAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_get_transfer_action_list_for_non_attack_phase(self):
        self.game_state.current_phase = GamePhase.FORTIFY
        actions = TransferAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_apply_transfer_action(self):
        action = TransferAction(3)
        new_state = action.apply(self.game_state, self.classic_map)

        self.assertEqual(new_state.territory_troops[0], 4)
        self.assertEqual(new_state.territory_troops[5], 3)
        self.assertEqual(new_state.current_territory_transfer, (-1, -1))

class TestFortifyRouteAction(TestAction):
    def setUp(self):
        super().setUp()

        self.game_state.current_phase = GamePhase.FORTIFY
        self.game_state.territory_troops = [5] * len(self.game_state.territory_troops) 
        self.game_state.territory_owners = [0] * len(self.game_state.territory_owners)
        self.game_state.territory_owners[34] = 1 # Siam being unowned by player 0 forces there to be two separate connected components of player-owned territories: Australia and the rest of the map
        
    def test_get_fortify_route_action_list(self):
        actions = FortifyRouteAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 1344) # Rest of world C.C + Australia C.C = (37 * 36) + (4 * 3) = 1344
    
    def test_get_fortify_route_action_list_for_insufficient_troop_counts(self):
        self.game_state.territory_troops = [1] * len(self.game_state.territory_troops)
        actions = FortifyRouteAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_get_fortify_route_action_list_for_no_connected_territories(self):
        self.game_state.current_player = 1
        actions = FortifyRouteAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0) # Player 1 only owns Siam, which has no connected territories to fortify to
    
    def test_get_fortify_route_action_list_for_non_fortify_phase(self):
        self.game_state.current_phase = GamePhase.ATTACK
        actions = FortifyRouteAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_apply_fortify_route_action(self):
        action = FortifyRouteAction(0, 1)
        new_state = action.apply(self.game_state, self.classic_map)

        self.assertEqual(new_state.current_fortify_route, (0, 1))
        self.assertEqual(new_state.current_phase, GamePhase.FORTIFY)
        self.assertEqual(new_state.territory_troops[0], 5)
        self.assertEqual(new_state.territory_troops[1], 5)
        self.assertEqual(len(FortifyRouteAction.get_action_list(new_state, self.classic_map)), 0) # only one FortifyRouteAction per turn
        self.assertEqual(len(FortifyAmountAction.get_action_list(new_state, self.classic_map)), 4)

class TestFortifyAmountAction(TestAction):
    def setUp(self):
        super().setUp()

        self.game_state.current_phase = GamePhase.FORTIFY
        self.game_state.territory_troops = [5] * len(self.game_state.territory_troops) 
        self.game_state.territory_owners = [0] * len(self.game_state.territory_owners)
        self.game_state.current_fortify_route = (0, 1)
        
    def test_get_fortify_amount_action_list(self):
        actions = FortifyAmountAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 4)
    
    def test_get_fortify_amount_action_list_while_no_fortify_route_pending(self):
        self.game_state.current_fortify_route = (-1, -1)
        actions = FortifyAmountAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_get_fortify_amount_action_list_for_non_fortify_phase(self):
        self.game_state.current_phase = GamePhase.ATTACK
        actions = FortifyAmountAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_apply_fortify_amount_action(self):
        action = FortifyAmountAction(3)
        new_state = action.apply(self.game_state, self.classic_map)

        self.assertEqual(new_state.territory_troops[0], 2)
        self.assertEqual(new_state.territory_troops[1], 8)
        self.assertEqual(new_state.current_phase, GamePhase.DRAFT)
        self.assertEqual(new_state.current_player, 1)

class TestSkipAction(TestAction):
    def setUp(self):
        super().setUp()
        self.game_state.current_phase = GamePhase.FORTIFY
        self.game_state.deployment_troops = 0
    
    def test_get_skip_action_list(self):
        actions = SkipAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 1)

    def test_get_skip_action_list_for_initial_state(self):
        self.game_state.reset_to_initial_state()
        actions = SkipAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0) # Skip action should not be available if there are troops to deploy during the draft phase
    
    def test_get_skip_action_list_after_battle_win(self):
        self.game_state.current_phase = GamePhase.ATTACK
        self.game_state.current_territory_transfer = (0, 5)
        actions = SkipAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_get_skip_action_list_during_current_fortify_route(self):
        self.game_state.current_fortify_route = (0, 1)
        actions = SkipAction.get_action_list(self.game_state, self.classic_map)
        self.assertEqual(len(actions), 0)
    
    def test_apply_skip_action_in_draft_phase(self):
        self.game_state.reset_to_initial_state()
        new_state = SkipAction().apply(DeployAction(0).apply(self.game_state, self.classic_map), self.classic_map)
        self.assertEqual(new_state.current_phase, GamePhase.ATTACK)
        self.assertEqual(new_state.current_player, 0)
    
    def test_apply_skip_action_in_attack_phase(self):
        self.game_state.current_phase = GamePhase.ATTACK
        new_state = SkipAction().apply(self.game_state, self.classic_map)
        self.assertEqual(new_state.current_phase, GamePhase.FORTIFY)
        self.assertEqual(new_state.current_player, 0)
    
    def test_apply_skip_action_in_fortify_phase(self):
        self.game_state.territory_captured_this_turn = True
        self.game_state.territory_owners = [0] * len(self.game_state.territory_owners)
        self.game_state.territory_owners[9], self.game_state.territory_owners[10], self.game_state.territory_owners[11], self.game_state.territory_owners[12] = 1, 1, 1, 1 # Give the next player owneship to all of South America
        new_state = SkipAction().apply(self.game_state, self.classic_map)

        self.assertEqual(len(new_state.player_territory_cards[0]), len(self.game_state.player_territory_cards[0]) + 1)
        self.assertFalse(new_state.territory_captured_this_turn)
        self.assertEqual(new_state.current_phase, GamePhase.DRAFT)
        self.assertEqual(new_state.current_player, 1)
        self.assertEqual(new_state.deployment_troops, 5) # 3 base troops + 2 for owning all of South America
    
    def test_apply_skip_action_in_fortify_phase_with_eliminations(self):
        self.game_state.active_players = [True, False, False, True] # Simulate players 1 and 2 being eliminated
        new_state = SkipAction().apply(self.game_state, self.classic_map)
        self.assertEqual(len(new_state.player_territory_cards[0]), len(self.game_state.player_territory_cards[0]))
        self.assertFalse(new_state.territory_captured_this_turn)
        self.assertEqual(new_state.current_phase, GamePhase.DRAFT)
        self.assertEqual(new_state.current_player, 3)

if __name__ == "__main__":
    unittest.main()

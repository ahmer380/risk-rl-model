import unittest

from src.environment.actions import BattleAction, TransferAction
from src.environment.game_state import GameState
from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.player_data import PlayerData

class TestBattleObserver(unittest.TestCase):
    def setUp(self):
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.num_players = 2
        self.game_state = GameState(self.num_players, len(self.classic_map.territories), True)
        self.battle_observer = BattleObserver(self.classic_map, [PlayerData(i) for i in range(self.num_players)])

        # Statically define territory ownership and troop counts to ensure consistent test results
        self.game_state.territory_owners = [1] * len(self.classic_map.territories)
        self.game_state.territory_troops = [2] * len(self.classic_map.territories)
        self.game_state.territory_owners[0], self.game_state.territory_owners[39] = 0, 0 # Player 0 owns Alaska and Indonesia
        self.game_state.territory_troops[0], self.game_state.territory_troops[40] = 100, 100 # 100 troops in Alaska and New Guinea

        # Player 0 will initiate battles from Alaska that always succeed
        self.run_battle_helper(0, 1) # Alaska attacks Alberta
        self.run_battle_helper(1, 6) # Alberta attacks Ontario
        self.run_battle_helper(6, 7) # Ontario attacks Quebec
        self.run_battle_helper(7, 4) # Quebec attacks Greenland

        # Player 0 will initiate battles that always fail
        self.run_battle_helper(39, 40) # Indonesia attacks New Guinea

    def run_battle_helper(self, attacker_territory_id: int, defender_territory_id: int):
        previous_state = self.game_state
        battle_action = BattleAction(attacker_territory_id, defender_territory_id)
        self.game_state = battle_action.apply(self.game_state, self.classic_map)
        self.battle_observer.on_action_taken(battle_action, previous_state, self.game_state)

        if self.game_state.current_territory_transfer == (attacker_territory_id, defender_territory_id):
            previous_state = self.game_state
            transfer_action = TransferAction(self.game_state.territory_troops[attacker_territory_id] - 1)
            self.game_state = transfer_action.apply(self.game_state, self.classic_map)
            self.battle_observer.on_action_taken(transfer_action, previous_state, self.game_state)
    
    def test_battle_win_rates(self):
        win_rates = self.battle_observer.get_battle_win_rates()
        self.assertEqual(win_rates[0], 4/5)
        self.assertEqual(win_rates[1], 0.0)
    
    def test_average_battles_per_turn(self):
        average_battles_per_turn = self.battle_observer.get_average_battles_per_turn()
        self.assertEqual(average_battles_per_turn[0], 5/1)
        self.assertEqual(average_battles_per_turn[1], 0.0)
    
    def test_territory_battle_counts(self):
        territory_battle_counts = self.battle_observer.get_territory_battle_counts()
        self.assertEqual(territory_battle_counts[self.classic_map.territories[1]], 1)
        self.assertEqual(territory_battle_counts[self.classic_map.territories[6]], 1)
        self.assertEqual(territory_battle_counts[self.classic_map.territories[7]], 1)
        self.assertEqual(territory_battle_counts[self.classic_map.territories[4]], 1)
        self.assertEqual(territory_battle_counts[self.classic_map.territories[40]], 1)

if __name__ == "__main__":
    unittest.main()
import unittest

from src.environment.game_state import GamePhase, GameState

class TestGameState(unittest.TestCase):
	def test_reset_to_initial_state(self):
		state = GameState(4, 42, True)
		state.reset_to_initial_state() # ensure operation is idempotent

		self.assertEqual(state.current_player, 0)
		self.assertEqual(state.current_phase, GamePhase.DRAFT)
		self.assertEqual(state.player_territory_cards, [[], [], [], []])
		self.assertEqual(state.trade_count, 0)
		self.assertEqual(state.deployment_troops, 3) # Territory partition is [11, 11, 10, 10], so each player gets 3 troops for deployment
		
		self.assertEqual(len(state.territory_owners), state.num_territories)
		self.assertEqual(len(state.territory_troops), state.num_territories)
		self.assertTrue(all(0 <= owner < state.num_players for owner in state.territory_owners)) # all territories owned
		self.assertTrue(all(troops >= 1 for troops in state.territory_troops)) # all territories have at least 1 troop

		territories_per_player = [0] * state.num_players
		troops_per_player = [0] * state.num_players
		for territory_i in range(state.num_territories):
			owner = state.territory_owners[territory_i]
			territories_per_player[owner] += 1
			troops_per_player[owner] += state.territory_troops[territory_i]

		self.assertLessEqual(max(territories_per_player) - min(territories_per_player), 1) # approx equal territories
		self.assertTrue(all(troops == troops_per_player[0] for troops in troops_per_player)) # equal troops

		self.assertFalse(state.is_terminal_state())

if __name__ == "__main__":
	unittest.main()

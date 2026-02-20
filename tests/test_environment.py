import unittest

from src.environment.environment import RiskEnvironment
from src.environment.map import RiskMap


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.map = RiskMap.from_json("maps/classic.json")
        self.env = RiskEnvironment(self.map, self.num_players)

    def test_random_game_simulation(self):
        for _ in range(10000):
            _, _, is_terminal = self.env.step(self.env.get_action_list().get_random_action())
            if is_terminal:
                break

if __name__ == '__main__':
    unittest.main()
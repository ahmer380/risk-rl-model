import unittest

import random

from src.environment.map import RiskMap
from src.environment.environment import RiskEnvironment

class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.env = RiskEnvironment(self.classic_map, self.num_players)

    def test_random_game_simulation(self):
        for i in range(100): # TODO: Fix DeployAction.getActionList() bottleneck!
            #print(f"Step = {i}, Current Player = {self.env.current_state.current_player}, Current Phase = {self.env.current_state.current_phase}")
            _, _, is_terminal = self.env.step(random.choice(self.env.get_action_list()))
            if is_terminal:
                break

if __name__ == '__main__':
    unittest.main()
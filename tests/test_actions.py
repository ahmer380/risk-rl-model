import unittest

from src.environment.game_state import GameState
from src.environment.map import RiskMap

class TestAction(unittest.TestCase):
    def setUp(self):
        self.num_players = 4
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.game_state = GameState(self.num_players, len(self.classic_map.territories), True)

class TestDeployAction(TestAction):
    pass

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

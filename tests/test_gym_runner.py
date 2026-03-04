import unittest

from src.agents.agent import RandomAgent, AdvantageAttackAgent

from src.environment.actions import DeployAction, TradeAction, BattleAction, TransferAction, FortifyRouteAction, FortifyAmountAction, SkipAction
from src.environment.map import RiskMap

from src.train.gym_runner import GymRunner
from src.train.rl_agent import RLAgent

class TestGymRunner(unittest.TestCase):
    def setUp(self):
        self.num_players = 6
        self.classic_map = RiskMap.from_json("maps/classic.json")
        self.runner = GymRunner(self.classic_map, [RLAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3), RandomAgent(4), AdvantageAttackAgent(5)])
    
    def test_max_actions(self):
        self.assertEqual(DeployAction.get_max_actions(self.classic_map), 42)
        self.assertEqual(TradeAction.get_max_actions(self.classic_map), 10)
        self.assertEqual(BattleAction.get_max_actions(self.classic_map), 1764)
        self.assertEqual(TransferAction.get_max_actions(self.classic_map), 1000)
        self.assertEqual(FortifyRouteAction.get_max_actions(self.classic_map), 1764)
        self.assertEqual(FortifyAmountAction.get_max_actions(self.classic_map), 1000)
        self.assertEqual(SkipAction.get_max_actions(self.classic_map), 1)
        self.assertEqual(self.runner.get_max_actions(), 5581)

class TestEncodeAndDecodeActions(TestGymRunner):
    def test_encode_and_decode_deploy_action(self):
        deploy_action = DeployAction(20)
        encoded = self.runner.encode_action(deploy_action)
        self.assertEqual(encoded, 20)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, deploy_action)
    
    def test_encode_and_decode_trade_action(self):
        trade_action = TradeAction([0, 3, 4])
        encoded = self.runner.encode_action(trade_action)
        self.assertEqual(encoded, 42 + 5)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, trade_action)
    
    def test_encode_and_decode_battle_action(self):
        battle_action = BattleAction(10, 15)
        encoded = self.runner.encode_action(battle_action)
        self.assertEqual(encoded, 42 + 10 + 435)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, battle_action)
    
    def test_encode_and_decode_transfer_action(self):
        transfer_action = TransferAction(50)
        encoded = self.runner.encode_action(transfer_action)
        self.assertEqual(encoded, 42 + 10 + 1764 + 50)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, transfer_action)
    
    def test_encode_and_decode_fortify_route_action(self):
        fortify_route_action = FortifyRouteAction(3, 31)
        encoded = self.runner.encode_action(fortify_route_action)
        self.assertEqual(encoded, 42 + 10 + 1764 + 1000 + 157)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, fortify_route_action)
    
    def test_encode_and_decode_fortify_amount_action(self):
        fortify_amount_action = FortifyAmountAction(1)
        encoded = self.runner.encode_action(fortify_amount_action)
        self.assertEqual(encoded, 42 + 10 + 1764 + 1000 + 1764 + 1)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, fortify_amount_action)
    
    def test_encode_and_decode_skip_action(self):
        skip_action = SkipAction()
        encoded = self.runner.encode_action(skip_action)
        self.assertEqual(encoded, self.runner.get_max_actions() - 1)
        decoded = self.runner.decode_action(encoded)
        self.assertEqual(decoded, skip_action)

if __name__ == "__main__":
    unittest.main()

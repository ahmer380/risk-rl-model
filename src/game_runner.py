
from src.agents.agent import Agent, RandomAgent, AdvantageAttackAgent

from src.environment.map import RiskMap
from src.environment.environment import RiskEnvironment

class GameRunner:
    def __init__(self, risk_map: RiskMap, agents: list[Agent], max_episode_length: int = 100000):
        assert [agent.player_id for agent in agents] == list(range(len(agents))), "Agent player IDs must be in order and match the number of agents."
        
        self.environment = RiskEnvironment(risk_map, len(agents))
        self.agents = agents
        self.max_episode_length = max_episode_length
    
    def run_episode(self):
        self.environment.reset()
        for agent in self.agents:
            agent.reset()

        is_terminal_state = False
        episode_length = 0

        while not is_terminal_state and episode_length < self.max_episode_length:
            _, _, is_terminal_state = self.environment.step(self.agents[self.environment.current_state.current_player].select_action(self.environment.get_action_list(), self.environment.current_state))
            episode_length += 1
        
        print(f"Episode ended after {episode_length} steps. Final state: \n{self.environment.current_state}")

risk_map = RiskMap.from_json("maps/classic.json")
agents = [AdvantageAttackAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3)]
game_runner = GameRunner(risk_map, agents)
game_runner.run_episode()

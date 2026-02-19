
from src.agents.agent import Agent, RandomAgent, AdvantageAttackAgent

from src.environment.map import RiskMap
from src.environment.environment import RiskEnvironment

from src.observer.game_observer import GameObserver

# TODO: Decide if a single GameRunner runs multiple episodes or if a new GameRunner is created for each episode. (address code inconsitencies)
class GameRunner:
    """Manages the execution of a SINGLE Risk game episode, coordinating between the environment, agents, and observer."""
    def __init__(self, risk_map: RiskMap, agents: list[Agent], game_observer: GameObserver = None, max_episode_length = 100000):
        assert [agent.player_id for agent in agents] == list(range(len(agents))), "Agent player IDs must be in order and match the number of agents."
        
        self.environment = RiskEnvironment(risk_map, len(agents))
        self.agents = agents
        self.game_observer = game_observer
        self.max_episode_length = max_episode_length
    
    def run_episode(self):
        self.environment.reset()
        for agent in self.agents:
            agent.reset()
        if self.game_observer:
            self.game_observer.on_game_start()

        is_terminal_state = False
        episode_length = 0

        while not is_terminal_state and episode_length < self.max_episode_length:
            previous_state = self.environment.current_state
            selected_action = self.agents[previous_state.current_player].select_action(self.environment.get_action_list(), previous_state)
            current_state, _, is_terminal_state = self.environment.step(selected_action)

            if self.game_observer:
                self.game_observer.on_action_taken(selected_action, previous_state, current_state)

            episode_length += 1
        
        if self.game_observer:
            self.game_observer.on_game_end(self.environment.current_state)

risk_map = RiskMap.from_json("maps/classic.json")
agents = [AdvantageAttackAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3)]
game_observer = GameObserver(risk_map, len(agents))
game_runner = GameRunner(risk_map, agents, game_observer)
game_runner.run_episode()
print(game_observer.summarise())
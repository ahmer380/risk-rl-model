
from src.agents.agent import Agent

from src.environment.map import RiskMap
from src.environment.environment import RiskEnvironment

from src.observers.observer_manager import ObserverManager

class GameRunner:
    """Manages the execution of a SINGLE Risk game episode, coordinating between the environment, agents, and observer."""
    def __init__(
        self,
        risk_map: RiskMap,
        agents: list[Agent],
        observer_manager: ObserverManager,
        max_episode_length: int,
    ):
        assert [agent.player_id for agent in agents] == list(range(len(agents))), "Agent player IDs must be in order and match the number of agents."
        
        self.environment = RiskEnvironment(risk_map, len(agents))
        self.agents = agents
        self.observer_manager = observer_manager
        self.max_episode_length = max_episode_length
    
    def run_episode(self):
        self.environment.reset()
        for agent in self.agents:
            agent.reset()
        self.observer_manager.notify_game_start()

        is_terminal_state = False
        episode_length = 0

        while not is_terminal_state and episode_length < self.max_episode_length:
            previous_state = self.environment.current_state
            action_list = self.environment.get_action_list()
            self.observer_manager.notify_action_list_generated(action_list)

            selected_action = self.agents[previous_state.current_player].select_action(action_list, previous_state)
            current_state, _, is_terminal_state = self.environment.step(selected_action)
            self.observer_manager.notify_action_taken(selected_action, previous_state, current_state)

            episode_length += 1

        self.observer_manager.notify_game_end(self.environment.current_state)

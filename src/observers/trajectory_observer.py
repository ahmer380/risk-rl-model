from src.environment.actions import Action
from src.environment.game_state import GameState

from src.observers.observer import Observer, CoreObserver

class TrajectoryItem:
    def __init__(self, state: GameState, action: Action, reward: float, next_state: GameState):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state
    
    def done(self) -> bool:
        return self.next_state.is_terminal_state()

class TrajectoryObserver(Observer):
    def __init__(self, core_observer: CoreObserver = None):
        super().__init__(core_observer)

        self.trajectory: list[TrajectoryItem] = []
    
    def on_action_taken(self, action: Action, previous_state: GameState, current_state: GameState, reward: float):
        self.trajectory.append(TrajectoryItem(previous_state, action, reward, current_state))
    
    def summarise_game(self) -> str:
        lines = ["#### Trajectory Observations ####"]

        lines.append(f"Trajectory list contains {len(self.trajectory)} items")

        return "\n".join(lines)
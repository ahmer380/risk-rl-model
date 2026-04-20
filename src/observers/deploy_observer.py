from typing import Self

from src.environment.actions import Action, DeployAction
from src.environment.game_state import GameState

from src.observers.observer import Observer
from src.observers.player_telemetry import DeployLog

class DeployObserver(Observer):
    """Observer for tracking deploy events for experimental analysis."""
    def on_action_taken(self, action: Action, previous_state: GameState, _: GameState):
        if isinstance(action, DeployAction):
            deploy_log = DeployLog(
                turn_number=self.core_observer.turn_count,
                player_id=previous_state.current_player,
                territory_id=action.territory_id
            )
            self.core_observer.player_telemetries[deploy_log.player_id].deployments.append(deploy_log)
    
    def summarise_game(self) -> str:
        return ""

    """Class methods for collecting and summarising aggregate outcome data for experimental anlaysis """
    
    @classmethod
    def summarise_simulation(cls, observers: list[Self], rl_agent_performance_test: bool = False) -> str:
        return ""
    
    @classmethod
    def get_deploy_logs(cls, observers: list[Self], player_name: str) -> list[DeployLog]:
        deploy_logs = []
        for observer in observers:
            player_telemetry = next((pt for pt in observer.core_observer.player_telemetries if pt.player_name == player_name))
            deploy_logs.extend(player_telemetry.deployments)
        return deploy_logs

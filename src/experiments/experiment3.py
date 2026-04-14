from matplotlib import pyplot as plt
from matplotlib.patches import Patch

from collections import defaultdict

from src.agents.agent import Agent

from src.environment.map import RiskMap

from src.observers.battle_observer import BattleObserver
from src.observers.deploy_observer import DeployObserver
from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

from src.train.rl_agent import RLAgent

from src.utils.k_clique_generator import KCliqueGenerator

class Experiment3:
    def __init__(
        self,
        risk_map: RiskMap,
        num_players: int,
        num_episodes: int = 10000
    ):
        self.risk_map = risk_map
        self.num_players = num_players
        self.num_episodes = num_episodes

        Agent.reset_player_ids()
        self.rl_agent = RLAgent(risk_map=self.risk_map, num_players=self.num_players)
        self.simulation_runner = SimulationRunner(
            title=f"RLAgent Performance Test on {self.risk_map.name} with {self.num_players} players",
            risk_map=self.risk_map,
            agents=[self.rl_agent],
            num_episodes=self.num_episodes,
            observers=[OutcomeObserver(), BattleObserver(), DeployObserver()],
            enable_rl_agent_performance_test=True,
            rl_agent_performance_test_num_players=self.num_players
        )
    
    def run_experiment(self):
        self.simulation_runner.run_simulation()
        self.simulation_runner.summarise_simulation()
    
    def plot_rl_win_rate_graph(self, ax: plt.Axes):
        outcome_observers = [
            next(observer for observer in observer_manager.observers if isinstance(observer, OutcomeObserver))
            for observer_manager in self.simulation_runner.game_observations
        ]
        rl_win_rate = OutcomeObserver.get_winner_distributions(outcome_observers, rl_agent_performance_test=True)[0][-2]
        ax.bar("RL Agent", rl_win_rate, color="darkblue")
        ax.bar("Other Agents", (100 - rl_win_rate), color="darkorange")
        ax.set_title("RL Agent Win Rate (%)")
        ax.set_ylim(0, 100)
    
    def plot_rl_battle_heatmap_graph(self, ax: plt.Axes):
        battle_observers = [
            next(observer for observer in observer_manager.observers if isinstance(observer, BattleObserver))
            for observer_manager in self.simulation_runner.game_observations
        ]

        rl_battle_logs = BattleObserver.get_battle_logs(battle_observers, player_name=self.rl_agent.get_name())
        territory_battle_counts: defaultdict[int, int] = defaultdict(int)
        for log in rl_battle_logs:
            territory_battle_counts[log.defender_territory_id] += 1

        for territory_id, count in sorted(territory_battle_counts.items()):
            ax.bar(self.risk_map.territories[territory_id].name, count / len(rl_battle_logs) * 100, color="darkgreen")
        
        ax.set_title("RL Agent Battle Distribution (%)")
        ax.set_xlabel("Territory")
    
    def plot_rl_deploy_heatmap_graph(self, ax: plt.Axes):
        deploy_observers = [
            next(observer for observer in observer_manager.observers if isinstance(observer, DeployObserver))
            for observer_manager in self.simulation_runner.game_observations
        ]

        rl_deploy_logs = DeployObserver.get_deploy_logs(deploy_observers, player_name=self.rl_agent.get_name())
        territory_deploy_counts: defaultdict[int, int] = defaultdict(int)
        for log in rl_deploy_logs:
            territory_deploy_counts[log.territory_id] += 1

        for territory_id, count in sorted(territory_deploy_counts.items()):
            ax.bar(self.risk_map.territories[territory_id].name, count / len(rl_deploy_logs) * 100, color="darkred")
        
        ax.set_title("RL Agent Deploy Distribution (%)")
        ax.set_xlabel("Territory")
    
    def plot_rl_battle_temporal_graph(self, ax: plt.Axes):
        MAX_TURNS = 50
        
        battle_observers = [
            next(observer for observer in observer_manager.observers if isinstance(observer, BattleObserver))
            for observer_manager in self.simulation_runner.game_observations
        ]
        rl_battle_logs = BattleObserver.get_battle_logs(battle_observers, player_name=self.rl_agent.get_name())

        outcome_observers = [
            next(observer for observer in observer_manager.observers if isinstance(observer, OutcomeObserver))
            for observer_manager in self.simulation_runner.game_observations
        ]
        average_turn_count = OutcomeObserver.get_game_length_statistics(outcome_observers)[1][2]

        battle_data_per_turn: dict[int, tuple[int, int]] = defaultdict(lambda: (0, 0)) # key=turn_number, value=(total_battle_count, total_battle_differential)
        for log in rl_battle_logs:
            if log.turn_number <= MAX_TURNS:
                battle_data_per_turn[log.turn_number] = (
                    battle_data_per_turn[log.turn_number][0] + 1,
                    battle_data_per_turn[log.turn_number][1] + log.attacker_troops - log.defender_troops
                )
        
        for turn in sorted(battle_data_per_turn.keys()):
            total_battle_count, total_battle_differential = battle_data_per_turn[turn]
            average_battle_differential = total_battle_differential / total_battle_count if total_battle_count > 0 else 0
            if average_battle_differential < 0:
                bar_color = "darkred"
            elif 0 <= average_battle_differential < 1:
                bar_color = "darkorange"
            elif 1 <= average_battle_differential < 2:
                bar_color = "orange"
            elif 2 <= average_battle_differential < 3:
                bar_color = "gold"
            elif 3 <= average_battle_differential < 5:
                bar_color = "yellowgreen"
            elif 5 <= average_battle_differential < 10:
                bar_color = "green"
            elif average_battle_differential >= 10:
                bar_color = "darkgreen"
            ax.bar(turn, total_battle_count / self.num_episodes, color=bar_color, alpha=0.6)
        
        ax.axvline(x=average_turn_count, color="black", linestyle="--", label=f"Average Game Length ({average_turn_count} turns)")

        legend_bins = [
            ("Disparity < 0", "darkred"),
            ("0 <= Disparity < 1", "darkorange"),
            ("1 <= Disparity < 2", "orange"),
            ("2 <= Disparity < 3", "gold"),
            ("3 <= Disparity < 5", "yellowgreen"),
            ("5 <= Disparity < 10", "green"),
            ("Disparity >= 10", "darkgreen"),
        ]
        legend_handles = [Patch(facecolor=color, alpha=0.6, label=label) for label, color in legend_bins]
        
        ax.set_title(f"RL Agent Average Battle Count per Turn (Up to Turn {MAX_TURNS})")
        ax.set_xlabel("Turn Number")
        ax.legend(handles=legend_handles, loc="upper right", title="Average Troop Disparity")
        ax.set_xlim(1, MAX_TURNS)
        ax.set_xticks([1] + list(range(5, MAX_TURNS + 1, 5)))
        
    def plot_results(self):
        fig, ax = plt.subplots(2, 2, figsize=(14, 8))
        fig.suptitle(f"RL Agent Performance Test on Map: {self.risk_map.name}", fontsize=14, fontweight='bold')

        self.plot_rl_win_rate_graph(ax[0, 0])
        self.plot_rl_battle_temporal_graph(ax[1, 1])
        self.plot_rl_deploy_heatmap_graph(ax[0, 1])
        self.plot_rl_battle_heatmap_graph(ax[1, 0])

        fig.tight_layout()
        fig.savefig(f"experiment_results/experiment3_{self.risk_map.name.lower()}")
        plt.show()

if __name__ == "__main__":
    experiment = Experiment3(risk_map=RiskMap.from_json(json_data=KCliqueGenerator.generate(k=8, density=0.25)), num_players=2)
    experiment.run_experiment()
    experiment.plot_results()

    experiment = Experiment3(risk_map=RiskMap.from_json(json_data=KCliqueGenerator.generate(k=8, density=1.0)), num_players=2)
    experiment.run_experiment()
    experiment.plot_results()

    experiment = Experiment3(risk_map=RiskMap.from_json(path="maps/mini.json"), num_players=2)
    experiment.run_experiment()
    experiment.plot_results()

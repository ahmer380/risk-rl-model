import os

from collections import defaultdict

import matplotlib.pyplot as plt

from src.agents.agent import Agent, RandomAgent

from src.environment.map import RiskMap

from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

from src.utils.k_clique_generator import KCliqueGenerator

class Experiment2:
    def __init__(
        self,
        map_size_start: int = 20,
        map_size_end: int = 100,
        map_size_interval: int = 1,
        map_density: float = 0.1,
        num_episodes_per_simulation: int = 1000,
    ):
        self.map_size_start = map_size_start
        self.map_size_end = map_size_end
        self.map_size_interval = map_size_interval
        self.map_density = map_density
        self.num_episodes_per_simulation = num_episodes_per_simulation

        self.map_sizes = list(range(self.map_size_start, self.map_size_end + 1, self.map_size_interval))
        self.simulations: dict[int, SimulationRunner] = {}
        self.stats: dict[str, list[float]] = defaultdict(list)

    def run_experiment(self):
        for map_size in self.map_sizes:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Running simulation for map size {map_size}/{self.map_size_end}")

            Agent.reset_player_ids()
            risk_map = RiskMap.from_json(json_data=KCliqueGenerator.generate(k=map_size, density=self.map_density))
            simulation_runner = SimulationRunner(
                title=f"Random vs Random fixed order - map size {map_size}",
                risk_map=risk_map,
                agents=[RandomAgent(), RandomAgent()],
                num_episodes=self.num_episodes_per_simulation,
                observers=[OutcomeObserver()],
                shuffle_turn_order=False,
            )
            simulation_runner.run_simulation()
            self.simulations[map_size] = simulation_runner

        self.calculate_stats()

    def calculate_stats(self):
        for map_size in sorted(self.simulations.keys()):
            simulation_runner = self.simulations[map_size]
            outcome_observers = [
                next(observer for observer in observer_manager.observers if isinstance(observer, OutcomeObserver))
                for observer_manager in simulation_runner.game_observations
            ]

            winner_distributions = OutcomeObserver.get_winner_distributions(outcome_observers)
            game_length_stats = OutcomeObserver.get_game_length_statistics(outcome_observers)

            player_1_name = outcome_observers[0].core_observer.player_telemetries[0].player_name
            player_1_distribution = next(row for row in winner_distributions if row[0] == player_1_name)

            self.stats["player_1_win_rate"].append(player_1_distribution[-2])
            self.stats["average_turn_count"].append(game_length_stats[1][2])
            self.stats["average_action_count"].append(game_length_stats[0][2])

    def add_common_plot_properties(self, ax: plt.Axes):
        ax.set_xlim(self.map_size_start, self.map_size_end)
        x_ticks = list(range(self.map_size_start, self.map_size_end + 1, 10))
        if self.map_size_end not in x_ticks:
            x_ticks.append(self.map_size_end)
        ax.set_xticks(x_ticks)
        ax.grid(True, alpha=0.3)

    def plot_player_1_win_rate_graph(self, ax: plt.Axes):
        ax.plot(self.map_sizes, self.stats["player_1_win_rate"], color="darkred")
        ax.set_ylim(0, 100)
        ax.set_title("Player 1 Win Rate (%) vs Map Size")
        ax.set_xlabel("Map Size (|M_T|)")
        ax.set_ylabel("Win Rate (%)")
        self.add_common_plot_properties(ax)

    def plot_turn_count_graph(self, ax: plt.Axes):
        ax.plot(self.map_sizes, self.stats["average_turn_count"], color="darkgreen")
        ax.set_title("Average Turn Count vs Map Size")
        ax.set_xlabel("Map Size (|M_T|)")
        ax.set_ylabel("Average Turn Count")
        self.add_common_plot_properties(ax)

    def plot_action_count_graph(self, ax: plt.Axes):
        ax.plot(self.map_sizes, self.stats["average_action_count"], color="darkblue")
        ax.set_title("Average Action Count vs Map Size")
        ax.set_xlabel("Map Size (|M_T|)")
        ax.set_ylabel("Average Action Count")
        self.add_common_plot_properties(ax)

    def plot_results(self):
        fig, axs = plt.subplots(1, 3, figsize=(18, 5))

        self.plot_player_1_win_rate_graph(axs[0])
        self.plot_turn_count_graph(axs[1])
        self.plot_action_count_graph(axs[2])

        fig.tight_layout()
        fig.savefig("experiment_results/experiment2")
        plt.show()


if __name__ == "__main__":
    experiment = Experiment2()
    experiment.run_experiment()
    experiment.plot_results()

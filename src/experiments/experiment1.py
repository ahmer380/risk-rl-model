import os

from collections import defaultdict

import matplotlib.pyplot as plt

from src.agents.agent import Agent, RandomAgent, CommunistAgent, CapitalistAgent

from src.environment.map import RiskMap

from src.observers.outcome_observer import OutcomeObserver

from src.runners.simulation_runner import SimulationRunner

from src.utils.k_clique_generator import KCliqueGenerator

"""
I am in a great spot to implement this experiment!

Then we can implement the experiment as follows:
1. Design a 16x16 complete graph, no continents (16 territories, 240 edges)
2. Implement a "map density" param to MapGenerator, between 0 and 1, which determines the proportion of edges that are kept in the graph.
  - 1: complete graph
  - k: smallest density that guarantees graph remains connected
3. Independent variable: map density (e.g. 0.1, 0.2, 0.3, ..., 1.0)
4. Dependent variable: take plots of (win rates per agent, average finish position, average action length, average turn length) against map density
5. Controlled variables: Agent compositon (communistAgent, capitalistAgent, 2 random agents), number of episodes (1000)

Threats to validity: (external validity)
- The results seem to change substantially depending on the values of "disparity" and "capitals"... just pick one, and say in "validity of results" section my findings of the fluctuations
- mention the realism to Risk a.k.a. the "four country limit" means density of 1 is impossible (oh well lol)
"""

class Experiment1:
    def __init__(
        self,
        clique_size: int,
        agent_composition: list[Agent],
        num_episodes_per_simulation: int = 1000,
        density_interval_size: float = 0.01
    ):
        self.clique_size = clique_size
        self.agent_composition = agent_composition
        self.num_episodes_per_simulation = num_episodes_per_simulation
        self.density_interval_size = density_interval_size

        self.simulations: dict[float, SimulationRunner] = {} # key=density, value=SimulationRunner with that density
        self.agent_stats: dict[Agent, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list)) # key=agent, value={key=metric name, value=metric value}
        self.game_length_stats: dict[str, list[float]] = defaultdict(list) # key=metric name, value=metric value
    
    def run_experiment(self):
        density = 2 / self.clique_size

        while density <= 1:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Running simulation for {self.clique_size}-Clique with Density {density:.2f}:")
            risk_map = RiskMap.from_json(json_data=KCliqueGenerator.generate(k=self.clique_size, density=density))
            simulation_runner = SimulationRunner(
                title=f"{self.clique_size}-Clique with Density {density:.2f} Simulation",
                risk_map=risk_map,
                agents=self.agent_composition,
                num_episodes=self.num_episodes_per_simulation,
                observers=[OutcomeObserver()],
                shuffle_turn_order=True
            )
            simulation_runner.run_simulation()
            self.simulations[density] = simulation_runner
            density = round(self.density_interval_size * (round(density / self.density_interval_size) + 1), 2)
      
        self.calculate_stats()
    
    def calculate_stats(self):
        """Calculate stats for each agent and overall game stats across all simulations"""
        densities = sorted(self.simulations.keys())

        for density in densities:
            simulation_runner = self.simulations[density]
            outcome_observers = [next(observer for observer in observer_manager.observers if isinstance(observer, OutcomeObserver)) for observer_manager in simulation_runner.game_observations]

            # Calculate win rate and average finish position for each agent
            winner_distributions = OutcomeObserver.get_winner_distributions(outcome_observers)
            for row in winner_distributions:
                agent_name = row[0]
                win_rate = row[-2]
                average_finish_position = row[-1]
                agent = next(agent for agent in self.agent_composition if agent.get_name() == agent_name)
                self.agent_stats[agent][f"win_rates"].append(win_rate)
                self.agent_stats[agent][f"average_finish_positions"].append(average_finish_position)
        
            # Calculate average, minimum, and maximum number of actions/turns per episode across all episodes in the simulation
            game_length_stats = OutcomeObserver.get_game_length_statistics(outcome_observers)
            average_actions, maximum_actions, minimum_actions = game_length_stats[0][2], game_length_stats[0][3], game_length_stats[0][4]
            average_turns, maximum_turns, minimum_turns = game_length_stats[1][2], game_length_stats[1][3], game_length_stats[1][4]
            self.game_length_stats[f"average_action_length"].append(average_actions)
            self.game_length_stats[f"maximum_action_length"].append(maximum_actions)
            self.game_length_stats[f"minimum_action_length"].append(minimum_actions)
            self.game_length_stats[f"average_turn_length"].append(average_turns)
            self.game_length_stats[f"maximum_turn_length"].append(maximum_turns)
            self.game_length_stats[f"minimum_turn_length"].append(minimum_turns)
    
    def add_common_plot_properties(self, ax: plt.Axes):
        """Plot the common base features for all graphs"""
        ax.set_xlim(2 /self.clique_size, 1)
        x_ticks = [density for density in self.simulations.keys() if density in [2 / self.clique_size, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels([f'{round(t, 3):g}' for t in x_ticks])
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)

    def plot_win_rate_graph(self, ax: plt.Axes):
        """Plot a map-density vs win rate graph for each agent across simulations"""
        for agent in self.agent_composition:
            win_rates = self.agent_stats[agent][f"win_rates"]
            densities = sorted(self.simulations.keys())
            ax.plot(densities, win_rates, label=agent.get_name(), color=agent.get_colour())
      
        ax.set_ylim(0, 100)
        ax.set_title("Win Rate (%) vs Map Density")
        self.add_common_plot_properties(ax)
    
    def plot_average_finish_position_graph(self, ax: plt.Axes):
        """Plot a map-density vs average finish position graph for each agent across simulations"""
        for agent in self.agent_composition:
            average_finish_positions = self.agent_stats[agent][f"average_finish_positions"]
            densities = sorted(self.simulations.keys())
            ax.plot(densities, average_finish_positions, label=agent.get_name(), color=agent.get_colour())
      
        ax.set_ylim(0, len(self.agent_composition))
        ax.set_title("Average Finish Position vs Map Density")
        self.add_common_plot_properties(ax)
    
    def plot_action_length_graph(self, ax: plt.Axes):
        """Plot a map-density vs average/maximum/minimum action length graph across simulations"""
        densities = sorted(self.simulations.keys())
        ax.plot(densities, self.game_length_stats[f"average_action_length"], label="Average", color="green")
        # ax.plot(densities, self.game_length_stats[f"maximum_action_length"], label="Maximum", color="red")
        # ax.plot(densities, self.game_length_stats[f"minimum_action_length"], label="Minimum", color="blue")

        ax.set_ylim(0, None)
        ax.set_title("Action Length vs Map Density")
        self.add_common_plot_properties(ax)
    
    def plot_turn_length_graph(self, ax: plt.Axes):
        """Plot a map-density vs average/maximum/minimum turn length graph across simulations"""
        densities = sorted(self.simulations.keys())
        ax.plot(densities, self.game_length_stats[f"average_turn_length"], label="Average", color="green")
        # ax.plot(densities, self.game_length_stats[f"maximum_turn_length"], label="Maximum", color="red")
        # ax.plot(densities, self.game_length_stats[f"minimum_turn_length"], label="Minimum", color="blue")

        ax.set_ylim(0, None)
        ax.set_title("Turn Length vs Map Density")
        self.add_common_plot_properties(ax)

if __name__ == "__main__":
    CLIQUE_SIZE = 16
    experiment = Experiment1(clique_size=CLIQUE_SIZE, agent_composition=[CommunistAgent(), CapitalistAgent(), RandomAgent(), RandomAgent()])
    experiment.run_experiment()

    fig, axs = plt.subplots(2, 2, figsize=(14, 8))
    experiment.plot_win_rate_graph(axs[0, 0])
    experiment.plot_average_finish_position_graph(axs[0, 1])
    experiment.plot_action_length_graph(axs[1, 0])
    experiment.plot_turn_length_graph(axs[1, 1])
    fig.tight_layout()
    fig.savefig(f"experiment_results/experiment1_{CLIQUE_SIZE}_clique")
    plt.show()

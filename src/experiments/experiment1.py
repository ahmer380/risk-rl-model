import os

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
      num_episodes_per_simulation: int = 10,
      density_interval_size: float = 0.05
    ):
      self.clique_size = clique_size
      self.agent_composition = agent_composition
      self.num_episodes_per_simulation = num_episodes_per_simulation
      self.density_interval_size = density_interval_size

      self.simulations: dict[float, SimulationRunner] = {} # density -> simulation runner
    
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

if __name__ == "__main__":
   experiment = Experiment1(clique_size=16, agent_composition=[CommunistAgent(), CapitalistAgent(), RandomAgent(), RandomAgent()])
   experiment.run_experiment()
   for simulation in experiment.simulations.values():
     simulation.summarise_simulation()

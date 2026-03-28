"""
I am in a great spot to implement this experiment!

A few pre-requisites:
1. Implement variable turn ordering in SimulationRunner. Order changes within each game
2. This in turn will let us decouple from the "player_id" parameter (i.e. shouldn't be used to get current_turn)

Then we can implement the experiment as follows:
1. Design a 16x16 complete graph, no continents (16 territories, 240 edges)
2. Implement a "map density" param to MapGenerator, between 0 and 1, which determines the proportion of edges that are kept in the graph.
  - 1: complete graph
  - k: smallest density that guarantees graph remains connected
3. Independent variable: map density (e.g. 0.1, 0.2, 0.3, ..., 1.0)
4. Dependent variable: take plots of (win rates per agent, average finish position, average action length, average turn length) against map density
5. Controlled variables: Agent compositon (communistAgent, capitalistAgent, 2 random agents), number of episodes (1000)

The results seem to change substantially depending on the values of "disparity" and "capitals"... just pick one, and say in "validity of results" section my findings of the fluctuations
"""
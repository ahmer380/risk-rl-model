import random

from src.agents.agent import Agent, RandomAgent, CommunistAgent, CapitalistAgent

class AgentSampler:
    """Utility class for sampling agents of various types."""
    @staticmethod
    def sample_agent() -> Agent:
        """Randomly sample an agent type and return an instance of that agent for the given player ID."""
        return random.choice([RandomAgent(), CommunistAgent(disparity=random.randint(0, 5)), CapitalistAgent(disparity=random.randint(0, 5))])

    @staticmethod
    def sample_agent_composition(num_players: int, min_agents: list[Agent] = []) -> list[Agent]:
        """Randomly sample a composition of agents for the given number of players."""
        assert len(min_agents) <= num_players, "Number of minimum agents cannot exceed total number of players"
        
        agents = min_agents + [AgentSampler.sample_agent() for _ in range(len(min_agents), num_players)]
        random.shuffle(agents)
        Agent.reset_player_ids()
        
        return agents

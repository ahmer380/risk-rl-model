import random

from src.agents.agent import Agent, RandomAgent, AdvantageAttackAgent

class AgentSampler:
    """Utility class for sampling agents of various types."""
    @staticmethod
    def sample_agent(player_id: int) -> Agent:
        """Randomly sample an agent type and return an instance of that agent for the given player ID."""
        return random.choice([RandomAgent, AdvantageAttackAgent])(player_id)

    @staticmethod
    def sample_agent_composition(num_players: int, min_agents: list[Agent] = []) -> list[Agent]:
        """Randomly sample a composition of agents for the given number of players."""
        assert len(min_agents) <= num_players, "Number of minimum agents cannot exceed total number of players"
        
        agents = min_agents + [AgentSampler.sample_agent(None) for _ in range(len(min_agents), num_players)]
        random.shuffle(agents)
        for player_id, agent in enumerate(agents):
            agent.player_id = player_id
        
        return agents

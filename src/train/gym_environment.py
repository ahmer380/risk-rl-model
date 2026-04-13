import numpy as np

import gymnasium

from src.agents.agent import Agent
from src.agents.agent_sampler import AgentSampler

from src.environment.actions import Action, ActionList, DeployAction, BattleFromAction, BattleToAction, TransferAction, FortifyFromAction, FortifyToAction, FortifyAmountAction, SkipAction
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap

class DummyRLAgent(Agent):
    """Placeholder agent used only to mark the RL-controlled slot within the environment"""
    def __init__(self):
        super().__init__(None, None, None)
    
    @classmethod
    def get_colour(cls):
        return "black"

class RiskGymEnvironment(gymnasium.Env):
    """The Gym environment for training a single RL agent to play Risk. This is NOT a general-purpose Risk environment and should never be used for experimentation outside of training the RL agent."""
    def __init__(self, risk_map: RiskMap, num_players: int, max_episode_length: int = 500):
        assert 2 <= num_players <= 6, "At least 2 and at most 6 agents are required to play Risk"

        self.risk_map = risk_map
        self.rl_agent = DummyRLAgent()
        self.agents = AgentSampler.sample_agent_composition(num_players=num_players, min_agents=[self.rl_agent])
        self.max_episode_length = max_episode_length # NOT the same as max game length, but how many steps the RL agent specifically will take

        self.episode_length = 0
        self.game_state = GameState(len(self.agents), len(risk_map.territories), reset_to_initial_state=True)
        self.game_state_at_start_of_rl_turn = None
        self.observation_space = self.get_observation_space()
        self.action_space = gymnasium.spaces.Discrete(self.get_max_actions(), dtype=np.uint16)

    def reset(self, seed: int=None):
        super().reset(seed=seed)

        self.agents = AgentSampler.sample_agent_composition(num_players=len(self.agents), min_agents=[self.rl_agent])
        self.episode_length = 0
        self.game_state.reset_to_initial_state()
        self.advance_to_rl_turn()
        self.game_state_at_start_of_rl_turn = self.game_state.copy()
        observation = self.encode_observation()
        info = {}

        return observation, info

    def step(self, action: int):
        """Apply a VALID action in the environment and return the resulting (observation, reward, terminated, truncated, info)."""
        # apply decoded action to the game state and advance to the next RL turn
        decoded_action = self.decode_action(action)
        previous_state = self.game_state
        self.game_state = decoded_action.apply(self.game_state, self.risk_map)
        self.advance_to_rl_turn()
        self.episode_length += 1
        observation = self.encode_observation()

        # calculate reward
        reward = self.calculate_reward(previous_state)

        # check if episode has terminated (i.e. game over, or RL agent eliminated)
        terminated = self.game_state.is_terminal_state() or not self.game_state.active_players[self.get_rl_agent_turn_number()]

        # check if episode has truncated (i.e. max episode length reached without termination)
        truncated = self.episode_length >= self.max_episode_length and not terminated

        info = {}
        if terminated or truncated:
            info["win"] = self.game_state.is_terminal_state() and self.game_state.get_winner() == self.get_rl_agent_turn_number()
            info["episode_length"] = self.episode_length

        return observation, reward, terminated, truncated, info

    def get_observation_space(self) -> gymnasium.Space:
        observation_space = gymnasium.spaces.Dict({
            "current_phase": gymnasium.spaces.MultiBinary(3), # one-hot encoding of the current phase (deploy, attack, fortify)
            "territories": gymnasium.spaces.Box( # [owned_by_rl_agent, troop_count_normalised] for each territory
                low=0.0,
                high=1.0,
                shape=(len(self.risk_map.territories), 2), 
                dtype=np.float32
            ),
            "territory_card_count": gymnasium.spaces.Box( # normalised count of how many territory cards the RL agent has
                low=0.0,
                high=1.0,
                shape=(1,), 
                dtype=np.float32
            ),
            "deployment_troops": gymnasium.spaces.Box( # normalised count of how many troops the RL agent has available to deploy
                low=0.0,
                high=1.0,
                shape=(1,),
                dtype=np.float32
            ),
        })

        return observation_space
    
    def encode_observation(self, inference=False) -> dict:
        if inference:
            rl_agent_turn_number = self.game_state.current_player
        else:
            rl_agent_turn_number = self.get_rl_agent_turn_number()
        total_troops = sum(self.game_state.territory_troops)

        encoded_observation = {
            "current_phase": np.arange(3) == self.game_state.current_phase.value,
            "territories": np.array([
                [int(territory_owner == rl_agent_turn_number), troop_count / total_troops]
                for territory_owner, troop_count in zip(self.game_state.territory_owners, self.game_state.territory_troops)
            ], dtype=np.float32),
            "territory_card_count": np.array([min(self.game_state.territory_card_counts[rl_agent_turn_number] / 3.0, 1.0)], dtype=np.float32),
            "deployment_troops": np.array([self.game_state.deployment_troops / (self.game_state.deployment_troops + total_troops)], dtype=np.float32)
        }

        return encoded_observation
    
    def get_max_actions(self) -> int:
        """size: 5T + 9, where T is the number of territories"""
        return DeployAction.get_max_actions(self.risk_map) + \
               BattleFromAction.get_max_actions(self.risk_map) + \
               BattleToAction.get_max_actions(self.risk_map) + \
               TransferAction.get_max_actions(self.risk_map) + \
               FortifyFromAction.get_max_actions(self.risk_map) + \
               FortifyToAction.get_max_actions(self.risk_map) + \
               FortifyAmountAction.get_max_actions(self.risk_map) + \
               SkipAction.get_max_actions(self.risk_map)
    
    def advance_to_rl_turn(self):
        while self.game_state.current_player != self.get_rl_agent_turn_number() and not self.game_state.is_terminal_state() and self.game_state.active_players[self.get_rl_agent_turn_number()]:
            action_list = ActionList.get_action_list(self.game_state, self.risk_map)
            selected_action = self.agents[self.game_state.current_player].select_action(action_list, self.game_state, self.risk_map)
            self.game_state = selected_action.apply(self.game_state, self.risk_map)
    
    def action_masks(self, action_list: ActionList = None) -> np.ndarray:
        action_mask = np.zeros(self.get_max_actions(), dtype=bool)

        if action_list is None:
            action_list = ActionList.get_action_list(self.game_state, self.risk_map)

        for action in action_list.flatten():
            action_mask[self.encode_action(action)] = True
        
        return action_mask
    
    def encode_action(self, action: Action) -> int:
        offset = 0
        for action_class in [DeployAction, BattleFromAction, BattleToAction, TransferAction, FortifyFromAction, FortifyToAction, FortifyAmountAction, SkipAction]:
            if isinstance(action, action_class):
                return offset + action.encode_action(self.risk_map)
            
            offset += action_class.get_max_actions(self.risk_map)

    def decode_action(self, action_index: int) -> Action:
        offset = 0
        for action_class in [DeployAction, BattleFromAction, BattleToAction, TransferAction, FortifyFromAction, FortifyToAction, FortifyAmountAction, SkipAction]:
            max_actions = action_class.get_max_actions(self.risk_map)
            if offset <= action_index < offset + max_actions:
                return action_class.decode_action(int(action_index - offset), self.risk_map)
            
            offset += max_actions
    
    def calculate_reward(self, previous_state: GameState) -> float:
        """Calculate the reward for the current state based on the previous state and action."""
        if self.game_state.get_winner() == self.get_rl_agent_turn_number():
            return 1.0
        elif not self.game_state.active_players[self.get_rl_agent_turn_number()]:
            return -1.0
        elif previous_state.current_phase == GamePhase.FORTIFY and self.game_state.current_phase == GamePhase.DRAFT:
            # Compare the game states between the start of the RL agent's nth and (n+1)th turns
            currently_owned_territories = self.game_state.get_player_owned_territory_ids(self.get_rl_agent_turn_number())
            currently_owned_troop_share = sum(self.game_state.territory_troops[territory_id] for territory_id in currently_owned_territories) /sum(self.game_state.territory_troops)
            previously_owned_territories = self.game_state_at_start_of_rl_turn.get_player_owned_territory_ids(self.get_rl_agent_turn_number())
            previously_owned_troop_share = sum(self.game_state_at_start_of_rl_turn.territory_troops[territory_id] for territory_id in previously_owned_territories) / sum(self.game_state_at_start_of_rl_turn.territory_troops)

            # calculated normalised deltas
            troop_share_delta = (currently_owned_troop_share - previously_owned_troop_share)
            territory_delta = (len(currently_owned_territories) - len(previously_owned_territories)) / len(self.risk_map.territories)
            continent_bonus_delta = (
                self.risk_map.get_player_continent_bonuses(self.get_rl_agent_turn_number(), self.game_state.territory_owners) -
                self.risk_map.get_player_continent_bonuses(self.get_rl_agent_turn_number(), self.game_state_at_start_of_rl_turn.territory_owners)
            ) / self.risk_map.get_total_continent_bonuses() if self.risk_map.get_total_continent_bonuses() > 0 else 0.0

            self.game_state_at_start_of_rl_turn = self.game_state.copy()

            return (
                0.5 * troop_share_delta + 
                0.6 * territory_delta + 
                0.7 * continent_bonus_delta
            )
        else: # intra-turn actions, as well as stalemates, get no reward
            return 0.0
    
    def get_rl_agent_turn_number(self) -> int:
        return next(i for i, agent in enumerate(self.agents) if agent == self.rl_agent)

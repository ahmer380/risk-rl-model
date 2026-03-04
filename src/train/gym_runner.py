import numpy as np

import gymnasium

from src.agents.agent import Agent

from src.environment.actions import Action, ActionList, DeployAction, TradeAction, BattleAction, TransferAction, FortifyRouteAction, FortifyAmountAction, SkipAction
from src.environment.game_state import GameState
from src.environment.map import RiskMap

from src.train.rl_agent import RLAgent

class GymRunner(gymnasium.Env):
    def __init__(self, risk_map: RiskMap, agents: list[Agent], max_episode_length: int = 20000):
        assert 2 <= len(agents) <= 6, "At least 2 and at most 6 agents are required to play Risk"
        assert [agent.player_id for agent in agents] == list(range(len(agents))), "Agent player IDs must be in order and match the number of agents."
        assert sum(1 for agent in agents if isinstance(agent, RLAgent)) == 1, "There must be exactly one RLAgent in the list of agents"

        self.risk_map = risk_map
        self.agents = agents
        self.rl_agent: RLAgent = next(agent for agent in agents if isinstance(agent, RLAgent))

        self.max_episode_length = max_episode_length # NOT the same as max game length, but how many steps the RL agent specifically will take
        self.episode_length = 0

        self.game_state = GameState(len(agents), len(risk_map.territories), reset_to_initial_state=True)

        self.observation_space = self.get_observation_space()
        self.action_space = gymnasium.spaces.Discrete(self.get_max_actions())

    def reset(self, seed: int=None):
        super().reset(seed=seed)

        for agent in self.agents:
            agent.reset()

        self.episode_length = 0
        self.game_state.reset_to_initial_state()
        self.advance_to_rl_turn(self.game_state)
        observation = self.encode_observation(self.game_state)
        info = {}

        return observation, info

    def step(self, action):
        """Apply a VALID action in the environment and return the resulting (observation, reward, terminated, truncated, info)."""
        # apply decoded action to the game state and advance to the next RL turn
        action = self.decode_action(action)
        previous_state = self.game_state
        self.game_state = action.apply(self.game_state, self.risk_map)
        self.advance_to_rl_turn()
        self.episode_length += 1
        observation = self.encode_observation()

        # calculate reward
        reward = self.calculate_reward(previous_state)

        # check if episode has terminated (i.e. game over, or RL agent eliminated)
        terminated = self.game_state.is_terminal_state() or self.episode_length >= self.max_episode_length or not self.game_state.active_players[self.rl_agent.player_id]

        # check if episode has truncated (i.e. max episode length reached without termination)
        truncated = self.episode_length >= self.max_episode_length and not terminated

        info = {}

        return observation, reward, terminated, truncated, info

    def get_observation_space(self) -> gymnasium.Space:
        observation_space = gymnasium.spaces.Dict({
            "active_players": gymnasium.spaces.MultiBinary(len(self.game_state.active_players)), 
            "current_player": gymnasium.spaces.Discrete(len(self.game_state.active_players), dtype=np.uint8),
            "current_phase": gymnasium.spaces.Discrete(3, dtype=np.uint8),
            "territory_owners": gymnasium.spaces.Box( #TODO: consider one-hot encoding?
                low=0, 
                high=len(self.game_state.active_players) - 1, 
                shape=(len(self.game_state.territory_owners),), 
                dtype=np.uint8 
            ),
            "territory_troops": gymnasium.spaces.Box( #TODO: consider one-hot encoding?
                low=0, 
                high=65535, 
                shape=(len(self.game_state.territory_troops),), 
                dtype=np.uint16
            ),
            "player_territory_cards": gymnasium.spaces.Box(
                low=-1, 
                high=len(self.game_state.territory_owners) - 1,
                shape=(len(self.game_state.active_players), 5, 2), # player_territory_cards[player_id[territory_card_index]] = [combat_arm, territory_id]
                dtype=np.int8
            ),
            "trade_count": gymnasium.spaces.Discrete(65535, dtype=np.uint16),
            "deployment_troops": gymnasium.spaces.Discrete(65535, dtype=np.uint16),
            "current_territory_transfer": gymnasium.spaces.Box(
                low=-1, 
                high=len(self.game_state.territory_owners) - 1, 
                shape=(2,), 
                dtype=np.int8
            ),
            "current_fortify_route": gymnasium.spaces.Box(
                low=-1, 
                high=len(self.game_state.territory_owners) - 1, 
                shape=(2,), 
                dtype=np.int8
            ),
            "territory_captured_this_turn": gymnasium.spaces.MultiBinary(1)
        })

        return observation_space
    
    def get_max_actions(self) -> int:
        return DeployAction.get_max_actions(self.risk_map) + \
               TradeAction.get_max_actions(self.risk_map) + \
               BattleAction.get_max_actions(self.risk_map) + \
               TransferAction.get_max_actions(self.risk_map) + \
               FortifyRouteAction.get_max_actions(self.risk_map) + \
               FortifyAmountAction.get_max_actions(self.risk_map) + \
               SkipAction.get_max_actions(self.risk_map)
    
    def advance_to_rl_turn(self):
        while self.game_state.current_player != self.rl_agent.player_id and not self.game_state.is_terminal_state():
            action_list = ActionList.get_action_list(self.game_state, self.risk_map)
            selected_action = self.agents[self.game_state.current_player].select_action(action_list, self.game_state)
            self.game_state = selected_action.apply(self.game_state, self.risk_map)
    
    def encode_observation(self) -> dict:
        encoded_observation = {
            "active_players": np.array(self.game_state.active_players, dtype=np.uint8),
            "current_player": np.uint8(self.game_state.current_player),
            "current_phase": np.uint8(self.game_state.current_phase.value),
            "territory_owners": np.array(self.game_state.territory_owners, dtype=np.uint8),
            "territory_troops": np.array(self.game_state.territory_troops, dtype=np.uint16),
            "player_territory_cards": np.array([[[card.combat_arm.value if card is not None else -1, card.territory_id if card is not None else -1] for card in player_cards] for player_cards in self.game_state.player_territory_cards], dtype=np.int8),
            "trade_count": np.uint16(self.game_state.trade_count),
            "deployment_troops": np.uint16(self.game_state.deployment_troops),
            "current_territory_transfer": np.array(self.game_state.current_territory_transfer, dtype=np.int8),
            "current_fortify_route": np.array(self.game_state.current_fortify_route, dtype=np.int8),
            "territory_captured_this_turn": np.array([self.game_state.territory_captured_this_turn], dtype=np.uint8)
        }

        return encoded_observation
    
    def get_action_mask(self) -> np.ndarray:
        action_mask = np.zeros(self.get_max_actions(), dtype=bool)

        for action in ActionList.get_action_list(self.game_state, self.risk_map).flatten():
            action_mask[self.encode_action(action)] = True
        
        return action_mask
    
    def encode_action(self, action: Action) -> int:
        offset = 0
        for action_class in [DeployAction, TradeAction, BattleAction, TransferAction, FortifyRouteAction, FortifyAmountAction, SkipAction]:
            if isinstance(action, action_class):
                return offset + action.encode_action(self.risk_map)
            
            offset += action_class.get_max_actions(self.risk_map)

    def decode_action(self, action_index: int) -> Action:
        offset = 0
        for action_class in [DeployAction, TradeAction, BattleAction, TransferAction, FortifyRouteAction, FortifyAmountAction, SkipAction]:
            max_actions = action_class.get_max_actions(self.risk_map)
            if offset <= action_index < offset + max_actions:
                return action_class.decode_action(action_index - offset, self.risk_map)
            
            offset += max_actions
    
    def calculate_reward(self, previous_state: GameState) -> float:
        """Calculate the reward for the current state based on the previous state."""
        return 0.0

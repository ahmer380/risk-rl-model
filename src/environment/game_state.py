import math
import random
from enum import Enum
from typing import Self

class GamePhase(Enum):
    DRAFT = 0
    ATTACK = 1
    FORTIFY = 2

class CombatArm(Enum):
    INFANTRY = 0
    CAVALRY = 1
    ARTILLERY = 2
    WILD = 3

class TerritoryCard:
    def __init__(self, combat_arm: CombatArm, territory_id: int):
        self.combat_arm = combat_arm
        self.territory_id = territory_id
    
    @classmethod
    def generate_random_card(cls, num_territories: int) -> Self:
        combat_arm = random.choice(list(CombatArm))
        territory_id = random.randint(0, num_territories - 1)
        return cls(combat_arm, territory_id)

    def __repr__(self):
        return f"TerritoryCard(combat_arm={self.combat_arm}, territory_id={self.territory_id})"

class GameState:
    """Map Agnostic Game State Representation for Risk. This is the "environment" that the agent will interact with, and should be decoupled from any specific map representation."""
    active_players: list[bool]
    current_player: int
    current_phase: GamePhase
    territory_owners: list[int] # Owner player index for each territory
    territory_troops: list[int] # Number of troops in each territory
    player_territory_cards: list[list[TerritoryCard]] # List of territory cards owned by each player (by index)
    trade_count: int # Number of trades that have been made so far (to determine trade-in values)
    deployment_troops: int # Number of troops available for deployment in the current draft phase
    current_territory_transfer: tuple[int, int] # Most recent (attacker_territory_id, defender_territory_id) for TransferAction
    territory_captured_this_turn: bool # Determines if current player receives a random territory card at the end of the turn
    
    def __init__(self, num_players: int, num_territories: int, reset_to_initial_state: bool = False):
        if reset_to_initial_state:
            self.reset_to_initial_state(num_players, num_territories)

    def reset_to_initial_state(self, num_players: int = None, num_territories: int = None):
        num_players = num_players if num_players is not None else len(self.active_players)
        num_territories = num_territories if num_territories is not None else len(self.territory_owners)
        assert num_players is not None, "num_players must be provided if active_players is not already initialized"
        assert num_territories is not None, "num_territories must be provided if territory_owners is not already initialized"

        self.active_players = [True] * num_players
        self.current_player = 0
        self.current_phase = GamePhase.DRAFT
        self.player_territory_cards = [[] for _ in range(num_players)]
        self.trade_count = 0
        self.deployment_troops = max(3, math.ceil(num_territories / num_players) // 3) # Continent bonuses should NOT materialise in initial state
        self.current_territory_transfer = (-1, -1)
        self.territory_captured_this_turn = False

        '''
        Perform random initial assignment of territories and troops, adhering to the following "fairness" rules:
         - All players must initially own the same number of troops
         - All players must approximately own the same number of territories
         - If possible, no two bordering territories are owned by the same player (IGNORE FOR NOW)
        '''
        # TODO: A reasonable initial heuristic, but extend to also accept static values 
        troops_per_player = max(1, round(num_territories / num_players)) * 4
        
        self.territory_owners = [-1] * num_territories
        self.territory_troops = [0] * num_territories

        territory_indices = list(range(num_territories))
        random.shuffle(territory_indices)

        # Initially assign 1 troop to each territory, and assign ownership in a round-robin manner
        for i, territory_i in enumerate(territory_indices):
            self.territory_owners[territory_i] = i % num_players
            self.territory_troops[territory_i] = 1
        
        # Distribute remaining troops to each player
        for player in range(num_players):
            player_territories = self.get_player_owned_territory_ids(player)
            remaining = troops_per_player - len(player_territories) # already assigned 1 troop each
            for i, territory_i in enumerate(player_territories):
                if remaining > 0:
                    troops_to_add = random.randint(0, remaining) if i != len(player_territories) - 1 else remaining
                    self.territory_troops[territory_i] += troops_to_add
                    remaining -= troops_to_add

    def is_terminal_state(self) -> bool:
        return sum(self.active_players) == 1

    def get_winner(self) -> int:
        if not self.is_terminal_state():
            return None
        
        return self.active_players.index(True) 
    
    def get_player_owned_territory_ids(self, player_i = None) -> list[int]:
        if player_i is None:
            player_i = self.current_player

        return [i for i, owner in enumerate(self.territory_owners) if owner == player_i]

    def copy(self) -> Self:
        new_state = GameState(len(self.active_players), len(self.territory_owners))
        new_state.active_players = self.active_players.copy()
        new_state.current_player = self.current_player
        new_state.current_phase = self.current_phase
        new_state.territory_owners = self.territory_owners.copy()
        new_state.territory_troops = self.territory_troops.copy()
        new_state.player_territory_cards = [territory_cards.copy() for territory_cards in self.player_territory_cards]
        new_state.trade_count = self.trade_count
        new_state.deployment_troops = self.deployment_troops
        new_state.current_territory_transfer = self.current_territory_transfer
        new_state.territory_captured_this_turn = self.territory_captured_this_turn

        return new_state

    def __str__(self):
        lines = []
        lines.append(f"Terminal state = {'Yes' if self.is_terminal_state() else 'No'}")
        lines.append(f"Active players = {self.active_players}")
        lines.append(f"Current player = {self.current_player}")
        lines.append(f"Current phase = {self.current_phase}")
        lines.append(f"Trade count = {self.trade_count}")
        lines.append(f"Deployment troops = {self.deployment_troops}")
        lines.append(f"Territory captured this turn = {'Yes' if self.territory_captured_this_turn else 'No'}")
        lines.append(f"Current territory transfer = {self.current_territory_transfer}")
        lines.append(f"Territory owners = {self.territory_owners}")
        lines.append(f"Territory troops = {self.territory_troops}")

        for player_i in range(len(self.active_players)):
            lines.append(f"Player {player_i} owns {len(self.get_player_owned_territory_ids(player_i))} territories with {sum(self.territory_troops[i] for i in self.get_player_owned_territory_ids(player_i))} total troops, and {len(self.player_territory_cards[player_i])} territory cards.")
        
        return "\n".join(lines)

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

"""Map Agnostic Game State Representation for Risk. This is the "environment" that the agent will interact with, and should be decoupled from any specific map representation."""
class GameState:
    num_players: int
    num_territories: int
    current_player: int
    current_phase: GamePhase
    territory_owners: list[int] # Owner player index for each territory
    territory_troops: list[int] # Number of troops in each territory
    player_territory_cards: list[list[TerritoryCard]] # List of territory cards owned by each player (by index)
    trade_count: int # Number of trades that have been made so far (to determine trade-in values)
    deployment_troops: int # Number of troops available for deployment in the current draft phase
    
    def __init__(self, num_players: int, num_territories: int, reset_to_initial_state: bool = False):
        self.num_players = num_players
        self.num_territories = num_territories
        if reset_to_initial_state:
            self.reset_to_initial_state()

    def reset_to_initial_state(self):
        self.current_player = 0
        self.current_phase = GamePhase.DRAFT
        self.player_territory_cards = [[] for _ in range(self.num_players)]
        self.trade_count = 0
        self.deployment_troops = max(3, math.ceil(self.num_territories / self.num_players) // 3) # Continent bonuses should NOT materialise in initial state

        '''
        Perform random initial assignment of territories and troops, adhering to the following "fairness" rules:
         - All players must initially own the same number of troops
         - All players must approximately own the same number of territories
         - If possible, no two bordering territories are owned by the same player (IGNORE FOR NOW)
        '''

        # TODO: A reasonable initial heuristic, but extend to also accept static values 
        troops_per_player = max(1, round(self.num_territories / self.num_players)) * 4
        
        self.territory_owners = [-1] * self.num_territories
        self.territory_troops = [0] * self.num_territories

        territory_indices = list(range(self.num_territories))
        random.shuffle(territory_indices)

        # Initially assign 1 troop to each territory, and assign ownership in a round-robin manner
        for i, territory_i in enumerate(territory_indices):
            self.territory_owners[territory_i] = i % self.num_players
            self.territory_troops[territory_i] = 1
        
        # Distribute remaining troops to each player
        for player in range(self.num_players):
            player_territories = self.get_player_owned_territory_ids(player)
            remaining = troops_per_player - len(player_territories) # already assigned 1 troop each
            for i, territory_i in enumerate(player_territories):
                if remaining > 0:
                    troops_to_add = random.randint(0, remaining) if i != len(player_territories) - 1 else remaining
                    self.territory_troops[territory_i] += troops_to_add
                    remaining -= troops_to_add

    def advance_phase(self):
        if self.current_phase == GamePhase.DRAFT:
            self.current_phase = GamePhase.ATTACK
        elif self.current_phase == GamePhase.ATTACK:
            self.current_phase = GamePhase.FORTIFY
        elif self.current_phase == GamePhase.FORTIFY:
            self.current_phase = GamePhase.DRAFT
            self.current_player = (self.current_player + 1) % self.num_players
    
    def is_terminal_state(self) -> bool:
        return all(territory_owner == self.territory_owners[0] for territory_owner in self.territory_owners)
    
    def get_player_owned_territory_ids(self, player_i = None) -> list[int]:
        if player_i is None:
            player_i = self.current_player

        return [i for i, owner in enumerate(self.territory_owners) if owner == player_i]

    def copy(self) -> Self:
        new_state = GameState(self.num_players, self.num_territories)
        new_state.current_player = self.current_player
        new_state.current_phase = self.current_phase
        new_state.territory_owners = self.territory_owners.copy()
        new_state.territory_troops = self.territory_troops.copy()
        new_state.player_territory_cards = [territory_cards.copy() for territory_cards in self.player_territory_cards] # TODO: Check if .copy() is sufficient
        new_state.trade_count = self.trade_count
        new_state.deployment_troops = self.deployment_troops
        return new_state

    def __str__(self):
        lines = []
        lines.append(f"Current player = {self.current_player}")
        lines.append(f"Current phase = {self.current_phase}")
        
        lines.append("Territories:")
        for i in range(self.num_territories):
            lines.append(f"{i}: Owner = {self.territory_owners[i]}, troop count = {self.territory_troops[i]}")
        
        for player_i in range(self.num_players):
            lines.append(f"Player {player_i} cards = {self.player_cards[player_i]}")
        
        lines.append(f"Trade count = {self.trade_count}")
        lines.append(f"Deployment troops = {self.deployment_troops}")
        lines.append(f"Terminal state = {'Yes' if self.is_terminal_state() else 'No'}")
        
        return "\n".join(lines)

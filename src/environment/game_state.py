from enum import Enum
import random

class GamePhase(Enum):
    DRAFT = 0
    ATTACK = 1
    FORTIFY = 2

class GameState:
    num_players: int
    num_territories: int
    current_player: int
    current_phase: GamePhase
    territory_owners: list[int] # Owner player index for each territory
    territory_troops: list[int] # Number of troops in each territory
    
    def __init__(self, num_players: int, num_territories: int):
        self.num_players = num_players
        self.num_territories = num_territories
        self.reset_to_initial_state()

    def reset_to_initial_state(self):
        self.current_player = 0
        self.current_phase = GamePhase.DRAFT

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
            player_territories = [i for i, territory_owner in enumerate(self.territory_owners) if territory_owner == player]
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

    def __str__(self):
        lines = []
        lines.append(f"Current_player={self.current_player}")
        lines.append(f"Phase={self.current_phase}")
        
        lines.append("Territories:")
        for i in range(self.num_territories):
            lines.append(f"{i}: owner={self.territory_owners[i]}, armies={self.territory_troops[i]}")

        lines.append(f"Terminal state = {'Yes' if self.is_terminal_state() else 'No'}")
        
        return "\n".join(lines)

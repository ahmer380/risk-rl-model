from abc import ABC, abstractmethod
from typing import Self

from src.environment.game_state import GamePhase, GameState

class Action(ABC):    
    @abstractmethod
    def apply(self, game_state: GameState) -> GameState:
        """Return a copy of the game state resulting from applying this action to the given game state."""
        pass

    @classmethod 
    @abstractmethod
    def get_action_list(cls, game_state: GameState) -> list[Self]:
        """Return a list of all valid actions of this type that can be applied to the given game state."""
        pass

class DeployAction(Action):
    def __init__(self, deployments: list[tuple[int, int]]):
        self.deployments = deployments  # List of (territory_id, troop_count)
    
    def apply(self, game_state: GameState) -> GameState:
        new_state = game_state.copy()

        for territory_id, troop_count in self.deployments:
            new_state.territory_troops[territory_id] += troop_count
            
        return new_state

    @classmethod
    def get_action_list(cls, game_state: GameState) -> list[Self]:
        if game_state.current_phase != GamePhase.DRAFT:
            return []
        
        owned_territory_ids = game_state.get_player_owned_territory_ids()

        actions = []
        def backtrack(i: int, remaining_troops: int, current_deployments: list[tuple[int, int]]):
            if remaining_troops == 0:
                actions.append(cls(current_deployments.copy()))
                return
            
            if i == len(owned_territory_ids):
                return
            
            for troop_count in range(1, remaining_troops + 1):
                current_deployments.append((owned_territory_ids[i], troop_count))
                backtrack(i + 1, remaining_troops - troop_count, current_deployments)
                current_deployments.pop()

            backtrack(i + 1, remaining_troops, current_deployments)

        backtrack(0, game_state.deployment_troops, [])
        return actions
    
    def __repr__(self):
        return f"DeployAction(deployments={self.deployments})"

class TradeAction(Action):
    def __init__(self, territory_cards: set[int]):
        self.territory_cards = territory_cards
    
    def apply(self, game_state: GameState) -> GameState:
        return NotImplementedError

    @classmethod
    def get_action_list(cls, game_state: GameState) -> list[Self]:
        if game_state.current_phase != GamePhase.DRAFT:
            return []
        
        return NotImplementedError

class BattleAction(Action):
    def __init__(self, attacker_territory_id: int, defender_territory_id: int):
        self.attacker_territory_id = attacker_territory_id
        self.defender_territory_id = defender_territory_id
    
    def apply(self, game_state: GameState) -> GameState:
        return NotImplementedError

    @classmethod
    def get_action_list(cls, game_state: GameState) -> list[Self]:
        if game_state.current_phase != GamePhase.ATTACK:
            return []
        
        return NotImplementedError

class TransferAction(Action):
    def __init__(self, src_territory_id: int, dst_territory_id: int, troop_count: int):
        self.src_territory_id = src_territory_id
        self.dst_territory_id = dst_territory_id
        self.troop_count = troop_count
    
    def apply(self, game_state: GameState) -> GameState:
        new_state = game_state.copy()

        new_state.territory_troops[self.dst_territory_id] += self.troop_count
        new_state.territory_troops[self.src_territory_id] -= self.troop_count
        
        return new_state

    @classmethod
    def get_action_list(cls, game_state: GameState) -> list[Self]:
        if game_state.current_phase != GamePhase.ATTACK:
            return []
        
        return NotImplementedError

class FortifyAction(Action):
    def __init__(self, src_territory_id: int, dst_territory_id: int, troop_count: int):
        self.src_territory_id = src_territory_id
        self.dst_territory_id = dst_territory_id
        self.troop_count = troop_count
    
    def apply(self, game_state: GameState) -> GameState:
        new_state = game_state.copy()

        new_state.territory_troops[self.dst_territory_id] += self.troop_count
        new_state.territory_troops[self.src_territory_id] -= self.troop_count
        new_state.advance_phase() # Always advance phase after fortify
        
        return new_state

    @classmethod
    def get_action_list(cls, game_state: GameState) -> list[Self]:
        if game_state.current_phase != GamePhase.FORTIFY:
            return []
        
        return NotImplementedError

class SkipAction(Action):
    def apply(self, game_state: GameState) -> GameState:
        new_state = game_state.copy()

        new_state.advance_phase()

        return new_state
    
    @classmethod
    def get_action_list(cls, _: GameState) -> list[Self]:
        return [cls()]
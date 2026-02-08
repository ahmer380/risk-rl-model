from abc import ABC, abstractmethod
from typing import Self
from itertools import combinations

from src.environment.map import RiskMap
from src.environment.game_state import GamePhase, GameState, CombatArm, TerritoryCard

from src.blitz_battle_simulator.blitz_battle_simulator import BlitzBattleSimulator

battle_simulator = BlitzBattleSimulator()

class Action(ABC):    
    @abstractmethod
    def apply(self, game_state: GameState) -> GameState:
        """Return a copy of the game state resulting from applying this action to the given game state."""
        pass

    @classmethod 
    @abstractmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        """Return a list of all valid actions of this type that can be applied to the given game state."""
        pass

class DeployAction(Action):
    def __init__(self, deployments: list[tuple[int, int]]):
        self.deployments = deployments  # List of (territory_id, troop_count)
    
    def apply(self, game_state: GameState) -> GameState:
        new_state = game_state.copy()

        new_state.deployment_troops = 0
        for territory_id, troop_count in self.deployments:
            new_state.territory_troops[territory_id] += troop_count
            
        return new_state

    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
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
    def __init__(self, territory_cards: list[TerritoryCard]):
        assert len(territory_cards) == 3, "Must trade exactly 3 cards"
        self.territory_cards = sorted(territory_cards, key=lambda card: card.territory_id)
    
    def apply(self, game_state: GameState) -> GameState:
        new_state = game_state.copy()

        for card in self.territory_cards:
            new_state.player_territory_cards[new_state.current_player].remove(card)
            if new_state.territory_owners[card.territory_id] == new_state.current_player:
                new_state.territory_troops[card.territory_id] += 2 # Bonus troops for trading in a card of a territory you own
        
        bonuses = [4, 6, 8, 10, 12, 15]
        new_state.deployment_troops += bonuses[new_state.trade_count] if new_state.trade_count < len(bonuses) else new_state.trade_count * 5 - 10
        new_state.trade_count += 1

        return new_state

    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.DRAFT:
            return []

        def is_valid_set(cards: tuple[TerritoryCard, TerritoryCard, TerritoryCard]) -> bool:
            combat_arms = {card.combat_arm for card in cards}
            return CombatArm.WILD in combat_arms or len(combat_arms) == 1 or len(combat_arms) == 3

        return [cls(list(cards)) for cards in combinations(game_state.player_territory_cards[game_state.current_player], 3) if is_valid_set(cards)]

class BattleAction(Action):
    def __init__(self, attacker_territory_id: int, defender_territory_id: int):
        self.attacker_territory_id = attacker_territory_id
        self.defender_territory_id = defender_territory_id
    
    def apply(self, game_state: GameState) -> GameState:
        new_state = game_state.copy()

        remaining_attacker_troops, remaining_defender_troops = battle_simulator.simulate_battle(game_state.territory_troops[self.attacker_territory_id], game_state.territory_troops[self.defender_territory_id])

        new_state.territory_troops[self.attacker_territory_id] = remaining_attacker_troops
        new_state.territory_troops[self.defender_territory_id] = remaining_defender_troops

        if remaining_defender_troops == 0: # Attacker wins battle
            previous_territory_owner = new_state.territory_owners[self.defender_territory_id]
            new_state.territory_owners[self.defender_territory_id] = new_state.current_player
            new_state.current_territory_transfer = (self.attacker_territory_id, self.defender_territory_id)
            new_state.territory_captured_this_turn = True

            if all(territory_owner != previous_territory_owner for territory_owner in new_state.territory_owners): # Defender is eliminated
                new_state.active_players[previous_territory_owner] = False
                new_state.player_territory_cards[new_state.current_player].extend(new_state.player_territory_cards[previous_territory_owner]) 
                new_state.player_territory_cards[previous_territory_owner] = []

                if new_state.is_terminal_state():
                    pass # TODO: Handle logic here? or in env?

        return new_state

    @classmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.ATTACK or game_state.current_territory_transfer != (-1, -1):
            return []
        
        actions = []
        for attacker_id in game_state.get_player_owned_territory_ids():
            if game_state.territory_troops[attacker_id] < 2: # Need at least 2 troops to attack
                continue
            
            for defender_id in risk_map.get_border_ids(attacker_id):
                if game_state.territory_owners[defender_id] != game_state.current_player:
                    actions.append(cls(attacker_id, defender_id))
        
        return actions

class TransferAction(Action):
    def __init__(self, troop_count: int):
        self.troop_count = troop_count
    
    def apply(self, game_state: GameState) -> GameState:
        new_state = game_state.copy()

        new_state.territory_troops[new_state.current_territory_transfer[0]] -= self.troop_count
        new_state.territory_troops[new_state.current_territory_transfer[1]] += self.troop_count
        new_state.current_territory_transfer = (-1, -1)
        
        return new_state

    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.ATTACK or game_state.current_territory_transfer == (-1, -1):
            return []
        
        return [cls(troop_count) for troop_count in range(1, game_state.territory_troops[game_state.current_territory_transfer[0]])] 

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
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.FORTIFY:
            return []
        
        return NotImplementedError

class SkipAction(Action):
    def apply(self, game_state: GameState) -> GameState:
        new_state = game_state.copy()

        new_state.advance_phase() # TODO: Disband method, put logic here instead

        return new_state
    
    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.current_phase == GamePhase.DRAFT and game_state.deployment_troops > 0:
            return []
        
        return [cls()]
    
    def __repr__(self):
        return "SkipAction()"
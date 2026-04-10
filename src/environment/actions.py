import random

from abc import ABC, abstractmethod
from typing import Self
from itertools import combinations

from src.environment.map import RiskMap
from src.environment.game_state import GamePhase, GameState, CombatArm, TerritoryCard

from src.utils.blitz_battle_simulator import BlitzBattleSimulator

battle_simulator = BlitzBattleSimulator()

MAX_TROOP_TRANSFER = 100 # Arbitrary cap on troop transfer/fortifyAmount actions. If 100, then transfer the maximum possible troops.
# TODO: Rework as percentage for all values? or some? (50%, 25% etc.)

class Action(ABC):    
    @abstractmethod
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        """Return a copy of the game state resulting from applying this action to the given game state."""
    
    @abstractmethod
    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        """Perform a series of assertions to confirm the validity of an action for the given game state"""

    @abstractmethod
    def encode_action(self, risk_map: RiskMap) -> int:
        """Uniquely identify this action within the action space. Reverse of decode_action."""
    
    @classmethod
    def decode_action(cls, action_index: int, risk_map: RiskMap) -> Self:
        """Return an instance of this action corresponding to the given action index. Reverse of encode_action."""

    @classmethod 
    @abstractmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        """Return a list of all valid actions of this type that can be applied to the given game state."""

    @classmethod
    def get_max_actions(cls, risk_map: RiskMap) -> int:
        """Return the maximum number of valid actions of this type that can be applied to any game state with the given risk map"""

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Return a string name for this action type."""

class DeployAction(Action):
    def __init__(self, territory_id: int):
        self.territory_id = territory_id
    
    def apply(self, game_state: GameState, _: RiskMap) -> GameState:
        self.validate_action(game_state, _)
        new_state = game_state.copy()

        new_state.territory_troops[self.territory_id] += 1
        new_state.deployment_troops -= 1
            
        return new_state
    
    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        assert game_state.current_phase == GamePhase.DRAFT, "Can only apply DeployAction during draft phase"
        assert game_state.deployment_troops > 0, "No deployment troops remaining"
        assert game_state.territory_owners[self.territory_id] == game_state.current_player, "Can only deploy to your own territories"
        assert 0 <= self.encode_action(risk_map) < self.get_max_actions(risk_map), "Encoded action index out of bounds"

    def encode_action(self, _: RiskMap) -> int:
        return self.territory_id

    @classmethod
    def decode_action(cls, action_index: int, _: RiskMap) -> Self:
        return cls(action_index)

    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.DRAFT or game_state.deployment_troops == 0:
            return []
        
        return [cls(territory_id) for territory_id in game_state.get_player_owned_territory_ids()]

    @classmethod
    def get_max_actions(cls, risk_map: RiskMap) -> int:
        return len(risk_map.territories)

    @classmethod
    def get_name(cls) -> str:
        return "DeployAction"
    
    def __repr__(self):
        return f"DeployAction(territory_id={self.territory_id})"
    
    def __eq__(self, other):
        return isinstance(other, DeployAction) and self.territory_id == other.territory_id

class TradeAction(Action):
    def __init__(self, territory_card_indexes: list[int]):
        self.territory_card_indexes = sorted(territory_card_indexes)
    
    def apply(self, game_state: GameState, _: RiskMap) -> GameState:
        self.validate_action(game_state, _)
        new_state = game_state.copy()

        for territory_card_index in self.territory_card_indexes:
            territory_card = new_state.player_territory_cards[new_state.current_player][territory_card_index]
            if new_state.territory_owners[territory_card.territory_id] == new_state.current_player:
                new_state.territory_troops[territory_card.territory_id] += 2 # Bonus troops for trading in a card of a territory you own
        
        new_state.player_territory_cards[new_state.current_player] = [card for i, card in enumerate(new_state.player_territory_cards[new_state.current_player]) if i not in self.territory_card_indexes] + [None] * 3 # Remove traded cards and add None placeholders to maintain list size
        
        bonuses = [4, 6, 8, 10, 12, 15]
        new_state.deployment_troops += bonuses[new_state.trade_count] if new_state.trade_count < len(bonuses) else min(new_state.trade_count * 5 - 10, 30)
        new_state.trade_count += 1

        return new_state
    
    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        assert game_state.current_phase == GamePhase.DRAFT, "Can only apply TradeAction during draft phase"
        assert len(self.territory_card_indexes) == 3, "Must trade exactly 3 cards"
        assert self.is_valid_set(game_state, tuple(self.territory_card_indexes)), "Invalid set of cards to trade"
        assert 0 <= self.encode_action(risk_map) < self.get_max_actions(risk_map), "Encoded action index out of bounds"

    def encode_action(self, _: RiskMap) -> int:
        i1, i2, i3 = self.territory_card_indexes

        if i1 == 0 and i2 == 1 and i3 == 2: return 0
        if i1 == 0 and i2 == 1 and i3 == 3: return 1
        if i1 == 0 and i2 == 1 and i3 == 4: return 2
        if i1 == 0 and i2 == 2 and i3 == 3: return 3
        if i1 == 0 and i2 == 2 and i3 == 4: return 4
        if i1 == 0 and i2 == 3 and i3 == 4: return 5
        if i1 == 1 and i2 == 2 and i3 == 3: return 6
        if i1 == 1 and i2 == 2 and i3 == 4: return 7
        if i1 == 1 and i2 == 3 and i3 == 4: return 8
        if i1 == 2 and i2 == 3 and i3 == 4: return 9

    @classmethod
    def decode_action(cls, action_index: int, _: RiskMap) -> Self:
        if action_index == 0: return cls([0, 1, 2])
        if action_index == 1: return cls([0, 1, 3])
        if action_index == 2: return cls([0, 1, 4])
        if action_index == 3: return cls([0, 2, 3])
        if action_index == 4: return cls([0, 2, 4])
        if action_index == 5: return cls([0, 3, 4])
        if action_index == 6: return cls([1, 2, 3])
        if action_index == 7: return cls([1, 2, 4])
        if action_index == 8: return cls([1, 3, 4])
        if action_index == 9: return cls([2, 3, 4])

    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.DRAFT: 
            return []

        return [cls(list(card_indexes)) for card_indexes in combinations(range(5), 3) if cls.is_valid_set(game_state, card_indexes)]
    
    @classmethod
    def is_valid_set(cls, game_state: GameState, card_indexes: tuple[int, int, int]) -> bool:
        if any(game_state.player_territory_cards[game_state.current_player][card_index] is None for card_index in card_indexes):
            return False
        
        combat_arms = {game_state.player_territory_cards[game_state.current_player][card_index].combat_arm for card_index in card_indexes}
        return CombatArm.WILD in combat_arms or len(combat_arms) == 1 or len(combat_arms) == 3
    
    @classmethod
    def get_max_actions(cls, _: RiskMap) -> int:
        return 10 # C(5, 3) = 10

    @classmethod
    def get_name(cls) -> str:
        return "TradeAction"
    
    def __repr__(self):
        return f"TradeAction(territory_cards={self.territory_card_indexes})"
    
    def __eq__(self, other):
        return isinstance(other, TradeAction) and self.territory_card_indexes == other.territory_card_indexes
    
class BattleFromAction(Action):
    def __init__(self, attacker_territory_id: int):
        self.attacker_territory_id = attacker_territory_id
    
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        self.validate_action(game_state, risk_map)
        new_state = game_state.copy()

        new_state.current_battle = (self.attacker_territory_id, -1)

        return new_state
    
    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        assert game_state.current_phase == GamePhase.ATTACK, "Can only apply BattleFromAction during attack phase"
        assert game_state.current_battle == (-1, -1), "Must resolve previous battle before attacking again"
        assert game_state.territory_owners[self.attacker_territory_id] == game_state.current_player, "Attacking territory must be owned by current player"
        assert game_state.territory_troops[self.attacker_territory_id] >= 2, "Attacking territory must have at least 2 troops to attack"
        assert any(game_state.territory_owners[border_id] != game_state.current_player for border_id in risk_map.get_border_ids(self.attacker_territory_id)), "Attacking territory must have at least one bordering enemy territory to attack"
        assert 0 <= self.encode_action(risk_map) < self.get_max_actions(risk_map), "Encoded action index out of bounds"
    
    def encode_action(self, _: RiskMap) -> int:
        return self.attacker_territory_id
    
    @classmethod
    def decode_action(cls, action_index: int, _: RiskMap) -> Self:
        return cls(action_index)

    @classmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.ATTACK or game_state.current_battle != (-1, -1):
            return []
        
        actions = []
        for attacker_territory_id in game_state.get_player_owned_territory_ids():
            if game_state.territory_troops[attacker_territory_id] >= 2 and any(game_state.territory_owners[border_id] != game_state.current_player for border_id in risk_map.get_border_ids(attacker_territory_id)):
                actions.append(cls(attacker_territory_id))
        
        return actions

    @classmethod
    def get_max_actions(cls, risk_map: RiskMap) -> int:
        return len(risk_map.territories)
    
    @classmethod
    def get_name(cls) -> str:
        return "BattleFromAction"
    
    def __repr__(self):
        return f"BattleFromAction(attacker_territory_id={self.attacker_territory_id})"
    
    def __eq__(self, other):
        return isinstance(other, BattleFromAction) and self.attacker_territory_id == other.attacker_territory_id

class BattleToAction(Action):
    def __init__(self, defender_territory_id: int):
        self.defender_territory_id = defender_territory_id
    
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        self.validate_action(game_state, risk_map)
        new_state = game_state.copy()

        attacker_territory_id = game_state.current_battle[0]
        remaining_attacker_troops, remaining_defender_troops = battle_simulator.simulate_battle(game_state.territory_troops[attacker_territory_id], game_state.territory_troops[self.defender_territory_id])

        new_state.territory_troops[attacker_territory_id] = remaining_attacker_troops
        new_state.territory_troops[self.defender_territory_id] = remaining_defender_troops

        if remaining_defender_troops == 0: # Attacker wins battle
            previous_territory_owner = new_state.territory_owners[self.defender_territory_id]
            new_state.territory_owners[self.defender_territory_id] = new_state.current_player
            new_state.current_battle = (attacker_territory_id, self.defender_territory_id)
            new_state.territory_captured_this_turn = True

            if all(territory_owner != previous_territory_owner for territory_owner in new_state.territory_owners): # Defender is eliminated
                new_state.active_players[previous_territory_owner] = False

                territory_cards_to_transfer = [card for card in new_state.player_territory_cards[previous_territory_owner] if card is not None]
                for territory_card in territory_cards_to_transfer:
                    if None in new_state.player_territory_cards[new_state.current_player]:
                        empty_card_index = new_state.player_territory_cards[new_state.current_player].index(None)
                        new_state.player_territory_cards[new_state.current_player][empty_card_index] = territory_card

                new_state.player_territory_cards[previous_territory_owner] = [None] * 5
        else: # Defender wins battle
            new_state.current_battle = (-1, -1)

        return new_state
    
    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        assert game_state.current_phase == GamePhase.ATTACK, "Can only apply BattleToAction during attack phase"
        assert game_state.current_battle[0] != -1 and game_state.current_battle[1] == -1, "Must apply BattleToAction after BattleFromAction and before TransferAction"
        assert game_state.territory_owners[self.defender_territory_id] != game_state.current_player, "Defending territory cannot be owned by current player"
        assert self.defender_territory_id in risk_map.get_border_ids(game_state.current_battle[0]), "Attacking and defending territories must be bordering"
        assert 0 <= self.encode_action(risk_map) < self.get_max_actions(risk_map), "Encoded action index out of bounds"

    def encode_action(self, _: RiskMap) -> int:
        return self.defender_territory_id
    
    @classmethod
    def decode_action(cls, action_index: int, _: RiskMap) -> Self:
        return cls(action_index)

    @classmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        attacker_territory_id = game_state.current_battle[0]
        if game_state.current_phase != GamePhase.ATTACK or attacker_territory_id == -1 or game_state.current_battle[1] != -1:
            return []
        
        actions = []
        for defender_territory_id in risk_map.get_border_ids(attacker_territory_id):
            if game_state.territory_owners[defender_territory_id] != game_state.current_player:
                actions.append(cls(defender_territory_id))
        
        return actions
    
    @classmethod
    def get_max_actions(cls, risk_map: RiskMap) -> int:
        return len(risk_map.territories)
    
    @classmethod
    def get_name(cls) -> str:
        return "BattleToAction"
    
    def __repr__(self):
        return f"BattleToAction(defender_territory_id={self.defender_territory_id})"
    
    def __eq__(self, other):
        return isinstance(other, BattleToAction) and self.defender_territory_id == other.defender_territory_id

class TransferAction(Action):
    def __init__(self, troop_count: int):
        self.troop_count = troop_count
    
    def apply(self, game_state: GameState, _: RiskMap) -> GameState:
        self.validate_action(game_state, _)
        new_state = game_state.copy()

        if self.troop_count == MAX_TROOP_TRANSFER:
            troops_to_transfer = new_state.territory_troops[new_state.current_battle[0]] - 1
        else:
            troops_to_transfer = self.troop_count
        
        new_state.territory_troops[new_state.current_battle[0]] -= troops_to_transfer
        new_state.territory_troops[new_state.current_battle[1]] += troops_to_transfer
        new_state.current_battle = (-1, -1)
        
        return new_state
    
    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        assert game_state.current_phase == GamePhase.ATTACK, "Can only apply TransferAction during attack phase"
        assert game_state.current_battle[0] != -1 and game_state.current_battle[1] != -1, "No territory transfer to resolve"
        assert 0 < self.troop_count < game_state.territory_troops[game_state.current_battle[0]], "Invalid troop count to transfer"
        assert 0 <= self.encode_action(risk_map) < self.get_max_actions(risk_map), "Encoded action index out of bounds"
    
    def encode_action(self, _: RiskMap) -> int:
        return self.troop_count
    
    @classmethod
    def decode_action(cls, action_index: int, _: RiskMap) -> Self:
        return cls(action_index)

    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.ATTACK or game_state.current_battle[0] == -1 or game_state.current_battle[1] == -1:
            return []
        
        return [cls(troop_count) for troop_count in range(1, min(MAX_TROOP_TRANSFER + 1, game_state.territory_troops[game_state.current_battle[0]]))]
    
    @classmethod
    def get_max_actions(cls, _: RiskMap) -> int:
        return MAX_TROOP_TRANSFER + 1 # 0-100 inclusive (although 0 is an invalid action)

    @classmethod
    def get_name(cls) -> str:
        return "TransferAction"
    
    def __repr__(self):
        return f"TransferAction(troop_count={self.troop_count})"

    def __eq__(self, other):
        return isinstance(other, TransferAction) and self.troop_count == other.troop_count

class FortifyFromAction(Action):
    def __init__(self, from_territory_id: int):
        self.from_territory_id = from_territory_id
    
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        self.validate_action(game_state, risk_map)
        new_state = game_state.copy()

        new_state.current_fortify = (self.from_territory_id, -1)

        return new_state

    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        assert game_state.current_phase == GamePhase.FORTIFY, "Can only apply FortifyFromAction during fortify phase"
        assert game_state.current_fortify == (-1, -1), "Must resolve previous fortify action before fortifying again"
        assert game_state.territory_owners[self.from_territory_id] == game_state.current_player, "From territory must be owned by current player"
        assert game_state.territory_troops[self.from_territory_id] >= 2, "From territory must have at least 2 troops to fortify"
        assert any(game_state.territory_owners[border_id] == game_state.current_player for border_id in risk_map.get_border_ids(self.from_territory_id)), "From territory must have at least one bordering friendly territory to fortify to"
        assert 0 <= self.encode_action(risk_map) < self.get_max_actions(risk_map), "Encoded action index out of bounds"
    
    def encode_action(self, _: RiskMap) -> int:
        return self.from_territory_id
    
    @classmethod
    def decode_action(cls, action_index: int, _: RiskMap) -> Self:
        return cls(action_index)
    
    @classmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.FORTIFY or game_state.current_fortify != (-1, -1):
            return []
        
        actions = []
        for from_territory_id in game_state.get_player_owned_territory_ids():
            if game_state.territory_troops[from_territory_id] >= 2 and any(game_state.territory_owners[border_id] == game_state.current_player for border_id in risk_map.get_border_ids(from_territory_id)):
                actions.append(cls(from_territory_id))
        
        return actions
    
    @classmethod
    def get_max_actions(cls, risk_map: RiskMap) -> int:
        return len(risk_map.territories)

    @classmethod
    def get_name(cls) -> str:
        return "FortifyFromAction"
    
    def __repr__(self):
        return f"FortifyFromAction(from_territory_id={self.from_territory_id})"

    def __eq__(self, other):
        return isinstance(other, FortifyFromAction) and self.from_territory_id == other.from_territory_id

class FortifyToAction(Action):
    def __init__(self, to_territory_id: int,):
        self.to_territory_id = to_territory_id
    
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        self.validate_action(game_state, risk_map)
        new_state = game_state.copy()

        new_state.current_fortify = (game_state.current_fortify[0], self.to_territory_id)

        return new_state
    
    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        assert game_state.current_phase == GamePhase.FORTIFY, "Can only apply FortifyToAction during fortify phase"
        assert game_state.current_fortify[0] != -1 and game_state.current_fortify[1] == -1, "Must apply FortifyToAction after FortifyFromAction and before FortifyAmountAction"
        assert game_state.current_fortify[0] != self.to_territory_id, "From and to territories cannot be the same"
        assert game_state.territory_owners[self.to_territory_id] == game_state.current_player, "To territory must be owned by current player"
        assert self.to_territory_id in self.get_connected_territories(game_state, risk_map, game_state.current_fortify[0], set()), "From and to territories must be connected"
        assert 0 <= self.encode_action(risk_map) < self.get_max_actions(risk_map), "Encoded action index out of bounds"
    
    def encode_action(self, _: RiskMap) -> int:
        return self.to_territory_id
    
    @classmethod
    def decode_action(cls, action_index: int, _: RiskMap) -> Self:
        return cls(action_index)

    @classmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.FORTIFY or game_state.current_fortify[0] == -1 or game_state.current_fortify[1] != -1:
            return []
        
        return [cls(to_territory_id) for to_territory_id in cls.get_connected_territories(game_state, risk_map, game_state.current_fortify[0], set()) - {game_state.current_fortify[0]}]

    @classmethod
    def get_connected_territories(cls, game_state: GameState, risk_map: RiskMap, territory_id: int, visited: set[int]) -> set[int]:
        visited.add(territory_id)
        connected_territories = {territory_id}
        for border_id in risk_map.get_border_ids(territory_id):
            if border_id not in visited and game_state.territory_owners[border_id] == game_state.current_player:
                connected_territories |= cls.get_connected_territories(game_state, risk_map, border_id, visited)

        return connected_territories

    @classmethod
    def get_max_actions(cls, risk_map: RiskMap) -> int:
        return len(risk_map.territories)
    
    @classmethod
    def get_name(cls) -> str:
        return "FortifyToAction"
    
    def __repr__(self):
        return f"FortifyToAction(to_territory_id={self.to_territory_id})"

    def __eq__(self, other):
        return isinstance(other, FortifyToAction) and self.to_territory_id == other.to_territory_id

class FortifyAmountAction(Action):
    def __init__(self, troop_count: int):
        self.troop_count = troop_count
    
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        self.validate_action(game_state, risk_map)
        new_state = game_state.copy()

        if self.troop_count == MAX_TROOP_TRANSFER:
            troops_to_fortify = new_state.territory_troops[new_state.current_fortify[0]] - 1
        else:
            troops_to_fortify = self.troop_count

        new_state.territory_troops[new_state.current_fortify[1]] += troops_to_fortify
        new_state.territory_troops[new_state.current_fortify[0]] -= troops_to_fortify
        new_state.current_fortify = (-1, -1)
        
        return SkipAction().apply(new_state, risk_map) # Skip to end turn after fortifying
    
    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        assert game_state.current_phase == GamePhase.FORTIFY, "Can only apply FortifyAmountAction during fortify phase"
        assert game_state.current_fortify[0] != -1 and game_state.current_fortify[1] != -1, "No fortify to resolve"
        assert 0 < self.troop_count < game_state.territory_troops[game_state.current_fortify[0]] or self.troop_count == MAX_TROOP_TRANSFER, "Invalid troop count to fortify"
        assert 0 <= self.encode_action(risk_map) < self.get_max_actions(risk_map), "Encoded action index out of bounds"
    
    def encode_action(self, _: RiskMap) -> int:
        return self.troop_count
    
    @classmethod
    def decode_action(cls, action_index: int, _: RiskMap) -> Self:
        return cls(action_index)

    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.FORTIFY or game_state.current_fortify[0] == -1 or game_state.current_fortify[1] == -1:
            return []
        
        return [cls(troop_count) for troop_count in range(1, min(MAX_TROOP_TRANSFER + 1, game_state.territory_troops[game_state.current_fortify[0]]))]
    
    @classmethod
    def get_name(cls) -> str:
        return "FortifyAmountAction"
    
    @classmethod
    def get_max_actions(cls, _: RiskMap) -> int:
        return MAX_TROOP_TRANSFER + 1 # 0-100 inclusive (although 0 is an invalid action)
    
    def __repr__(self):
        return f"FortifyAmountAction(troop_count={self.troop_count})"
    
    def __eq__(self, other):
        return isinstance(other, FortifyAmountAction) and self.troop_count == other.troop_count

class SkipAction(Action):
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        self.validate_action(game_state, risk_map)
        new_state = game_state.copy()

        if new_state.current_phase == GamePhase.DRAFT:
            new_state.current_phase = GamePhase.ATTACK
        elif new_state.current_phase == GamePhase.ATTACK:
            new_state.current_phase = GamePhase.FORTIFY
        elif new_state.current_phase == GamePhase.FORTIFY:
            # Draw random territory card if player captured a territory this turn
            if new_state.territory_captured_this_turn:
                if None in new_state.player_territory_cards[new_state.current_player]:
                    empty_card_index = new_state.player_territory_cards[new_state.current_player].index(None)
                    new_state.player_territory_cards[new_state.current_player][empty_card_index] = TerritoryCard.generate_random_card(len(new_state.territory_owners))
                new_state.territory_captured_this_turn = False
            
            new_state.current_phase = GamePhase.DRAFT
            new_state.current_player = (new_state.current_player + 1) % len(new_state.active_players)
            while new_state.active_players[new_state.current_player] == False:
                new_state.current_player = (new_state.current_player + 1) % len(new_state.active_players)
            
            # Calculate deployment troops for next player
            new_state.deployment_troops = max(3, len(new_state.get_player_owned_territory_ids()) // 3) + risk_map.get_player_continent_bonuses(new_state.current_player, new_state.territory_owners)

        return new_state
    
    def validate_action(self, game_state: GameState, risk_map: RiskMap):
        if game_state.current_phase == GamePhase.DRAFT:
            assert game_state.deployment_troops == 0, "Must deploy all troops before skipping"
        elif game_state.current_phase == GamePhase.ATTACK:
            assert game_state.current_battle == (-1, -1), "Must resolve battle before skipping"
        elif game_state.current_phase == GamePhase.FORTIFY:
            assert game_state.current_fortify == (-1, -1), "Must resolve fortify before skipping"
        assert 0 <= self.encode_action(risk_map) < self.get_max_actions(risk_map), "Encoded action index out of bounds"
    
    def encode_action(self, _: RiskMap) -> int:
        return 0
    
    @classmethod
    def decode_action(cls, _action_index: int, _risk_map: RiskMap) -> Self:
        return cls()
    
    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.deployment_troops > 0 or game_state.current_battle != (-1, -1) or game_state.current_fortify != (-1, -1):
            return []
        
        return [cls()]
    
    @classmethod
    def get_max_actions(cls, _: RiskMap) -> int:
        return 1
    
    @classmethod
    def get_name(cls) -> str:
        return "SkipAction"
    
    def __repr__(self):
        return "SkipAction()"
    
    def __eq__(self, other):
        return isinstance(other, SkipAction)

class ActionList:
    """Store a segmented list of all available actions for a given game state."""
    def __init__(
        self, 
        deploy_actions: list[DeployAction],
        trade_actions: list[TradeAction],
        battle_from_actions: list[BattleFromAction],
        battle_to_actions: list[BattleToAction],
        transfer_actions: list[TransferAction],
        fortify_from_actions: list[FortifyFromAction],
        fortify_to_actions: list[FortifyToAction],
        fortify_amount_actions: list[FortifyAmountAction],
        skip_actions: list[SkipAction]
    ):
        self.deploy_actions = deploy_actions
        self.trade_actions = trade_actions
        self.battle_from_actions = battle_from_actions
        self.battle_to_actions = battle_to_actions
        self.transfer_actions = transfer_actions
        self.fortify_from_actions = fortify_from_actions
        self.fortify_to_actions = fortify_to_actions
        self.fortify_amount_actions = fortify_amount_actions
        self.skip_actions = skip_actions
    
    @classmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> Self:
        return cls(
            deploy_actions=DeployAction.get_action_list(game_state, risk_map),
            trade_actions=TradeAction.get_action_list(game_state, risk_map),
            battle_from_actions=BattleFromAction.get_action_list(game_state, risk_map),
            battle_to_actions=BattleToAction.get_action_list(game_state, risk_map),
            transfer_actions=TransferAction.get_action_list(game_state, risk_map),
            fortify_from_actions=FortifyFromAction.get_action_list(game_state, risk_map),
            fortify_to_actions=FortifyToAction.get_action_list(game_state, risk_map),
            fortify_amount_actions=FortifyAmountAction.get_action_list(game_state, risk_map),
            skip_actions=SkipAction.get_action_list(game_state, risk_map)
        )
    
    def get_random_action(self) -> Action:
        return random.choice(self.flatten())

    def get_uniform_random_action(self) -> Action:
        action_types = [
            self.deploy_actions,
            self.trade_actions,
            self.battle_from_actions,
            self.battle_to_actions,
            self.transfer_actions,
            self.fortify_from_actions,
            self.fortify_to_actions,
            self.fortify_amount_actions,
            self.skip_actions
        ]
        non_empty_action_types = [action_type for action_type in action_types if len(action_type) > 0]

        return random.choice(random.choice(non_empty_action_types))
    
    def get_action_type_list_by_name(self, action_name: str) -> list[Action]:
        if action_name == DeployAction.get_name():
            return self.deploy_actions
        elif action_name == TradeAction.get_name():
            return self.trade_actions
        elif action_name == BattleFromAction.get_name():
            return self.battle_from_actions
        elif action_name == BattleToAction.get_name():
            return self.battle_to_actions
        elif action_name == TransferAction.get_name():
            return self.transfer_actions
        elif action_name == FortifyFromAction.get_name():
            return self.fortify_from_actions
        elif action_name == FortifyToAction.get_name():
            return self.fortify_to_actions
        elif action_name == FortifyAmountAction.get_name():
            return self.fortify_amount_actions
        elif action_name == SkipAction.get_name():
            return self.skip_actions
        else:
            raise ValueError(f"Invalid action name: {action_name}")
        
    def size(self) -> int:
        return len(self.deploy_actions) + len(self.trade_actions) + len(self.battle_from_actions) + len(self.battle_to_actions) + len(self.transfer_actions) + len(self.fortify_from_actions) + len(self.fortify_to_actions) + len(self.fortify_amount_actions) + len(self.skip_actions)
    
    def flatten(self) -> list[Action]:
        return self.deploy_actions + self.trade_actions + self.battle_from_actions + self.battle_to_actions + self.transfer_actions + self.fortify_from_actions + self.fortify_to_actions + self.fortify_amount_actions + self.skip_actions

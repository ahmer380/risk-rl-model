from abc import ABC, abstractmethod
from typing import Self
from itertools import combinations

from src.environment.map import RiskMap
from src.environment.game_state import GamePhase, GameState, CombatArm, TerritoryCard

from src.blitz_battle_simulator.blitz_battle_simulator import BlitzBattleSimulator

battle_simulator = BlitzBattleSimulator()

class Action(ABC):    
    @abstractmethod
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        """Return a copy of the game state resulting from applying this action to the given game state."""
        pass

    @classmethod 
    @abstractmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        """Return a list of all valid actions of this type that can be applied to the given game state."""
        pass

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Return a string name for this action type."""

class DeployAction(Action):
    def __init__(self, territory_id: int):
        self.territory_id = territory_id
    
    def apply(self, game_state: GameState, _: RiskMap) -> GameState:
        new_state = game_state.copy()

        new_state.territory_troops[self.territory_id] += 1
        new_state.deployment_troops -= 1
            
        return new_state

    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.DRAFT or game_state.deployment_troops == 0:
            return []
        
        return [cls(territory_id) for territory_id in game_state.get_player_owned_territory_ids()]

    @classmethod
    def get_name(cls) -> str:
        return "DeployAction"
    
    def __repr__(self):
        return f"DeployAction(territory_id={self.territory_id})"

class TradeAction(Action):
    def __init__(self, territory_cards: list[TerritoryCard]):
        assert len(territory_cards) == 3, "Must trade exactly 3 cards"
        self.territory_cards = sorted(territory_cards, key=lambda card: card.territory_id)
    
    def apply(self, game_state: GameState, _: RiskMap) -> GameState:
        new_state = game_state.copy()

        for card in self.territory_cards:
            new_state.player_territory_cards[new_state.current_player].remove(card)
            if new_state.territory_owners[card.territory_id] == new_state.current_player:
                new_state.territory_troops[card.territory_id] += 2 # Bonus troops for trading in a card of a territory you own
        
        bonuses = [4, 6, 8, 10, 12, 15]
        new_state.deployment_troops += bonuses[new_state.trade_count] if new_state.trade_count < len(bonuses) else min(new_state.trade_count * 5 - 10, 30)
        new_state.trade_count += 1

        return new_state

    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.DRAFT or len(game_state.player_territory_cards[game_state.current_player]) < 3:
            return []

        def is_valid_set(cards: tuple[TerritoryCard, TerritoryCard, TerritoryCard]) -> bool:
            combat_arms = {card.combat_arm for card in cards}
            return CombatArm.WILD in combat_arms or len(combat_arms) == 1 or len(combat_arms) == 3

        return [cls(list(cards)) for cards in combinations(game_state.player_territory_cards[game_state.current_player], 3) if is_valid_set(cards)]
    
    @classmethod
    def get_name(cls) -> str:
        return "TradeAction"
    
    def __repr__(self):
        return f"TradeAction(territory_cards={self.territory_cards})"

class BattleAction(Action):
    def __init__(self, attacker_territory_id: int, defender_territory_id: int):
        self.attacker_territory_id = attacker_territory_id
        self.defender_territory_id = defender_territory_id
    
    def apply(self, game_state: GameState, _: RiskMap) -> GameState:
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
    
    @classmethod
    def get_name(cls) -> str:
        return "BattleAction"
    
    def __repr__(self):
        return f"BattleAction(attacker_territory_id={self.attacker_territory_id}, defender_territory_id={self.defender_territory_id})"

class TransferAction(Action):
    def __init__(self, troop_count: int):
        self.troop_count = troop_count
    
    def apply(self, game_state: GameState, _: RiskMap) -> GameState:
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
    
    @classmethod
    def get_name(cls) -> str:
        return "TransferAction"
    
    def __repr__(self):
        return f"TransferAction(troop_count={self.troop_count})"

class FortifyAction(Action):
    def __init__(self, from_territory_id: int, to_territory_id: int, troop_count: int):
        self.from_territory_id = from_territory_id
        self.to_territory_id = to_territory_id
        self.troop_count = troop_count
    
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        new_state = game_state.copy()

        new_state.territory_troops[self.to_territory_id] += self.troop_count
        new_state.territory_troops[self.from_territory_id] -= self.troop_count

        return SkipAction().apply(new_state, risk_map) # Skip to end turn after fortifying

    @classmethod
    def get_action_list(cls, game_state: GameState, risk_map: RiskMap) -> list[Self]:
        if game_state.current_phase != GamePhase.FORTIFY:
            return []
        
        visited: set[int] = set()
        def get_connected_territories(territory_id) -> set[int]:
            visited.add(territory_id)
            connected_territories = {territory_id}
            for border_id in risk_map.get_border_ids(territory_id):
                if border_id not in visited and game_state.territory_owners[border_id] == game_state.current_player:
                    connected_territories |= get_connected_territories(border_id)

            return connected_territories

        visited.clear()
        actions = []
        for territory_id in game_state.get_player_owned_territory_ids():
            if territory_id in visited:
                continue

            connected_territories = get_connected_territories(territory_id)

            for from_id in connected_territories:
                for to_id in connected_territories:
                    if from_id != to_id:
                        for troop_count in range(1, game_state.territory_troops[from_id]):
                            actions.append(cls(from_id, to_id, troop_count))

            visited |= connected_territories

        return actions
    
    @classmethod
    def get_name(cls) -> str:
        return "FortifyAction"
    
    def __repr__(self):
        return f"FortifyAction(from_territory_id={self.from_territory_id}, to_territory_id={self.to_territory_id}, troop_count={self.troop_count})"

class SkipAction(Action):
    def apply(self, game_state: GameState, risk_map: RiskMap) -> GameState:
        new_state = game_state.copy()

        if new_state.current_phase == GamePhase.DRAFT:
            new_state.current_phase = GamePhase.ATTACK
        elif new_state.current_phase == GamePhase.ATTACK:
            new_state.current_phase = GamePhase.FORTIFY
        elif new_state.current_phase == GamePhase.FORTIFY:
            # Draw random territory card if player captured a territory this turn
            if new_state.territory_captured_this_turn: 
                new_state.player_territory_cards[new_state.current_player].append(TerritoryCard.generate_random_card(len(new_state.territory_owners)))
                new_state.territory_captured_this_turn = False
            
            new_state.current_phase = GamePhase.DRAFT
            new_state.current_player = (new_state.current_player + 1) % len(new_state.active_players)
            while new_state.active_players[new_state.current_player] == False:
                new_state.current_player = (new_state.current_player + 1) % len(new_state.active_players)
            
            # Calculate deployment troops for next player
            new_state.deployment_troops = max(3, len(new_state.get_player_owned_territory_ids()) // 3)
            for continent in risk_map.continents.values():
                if all(new_state.territory_owners[territory.id] == new_state.current_player for territory in continent.territories):
                    new_state.deployment_troops += continent.bonus

        return new_state
    
    @classmethod
    def get_action_list(cls, game_state: GameState, _: RiskMap) -> list[Self]:
        if (game_state.current_phase == GamePhase.DRAFT and game_state.deployment_troops > 0) or game_state.current_territory_transfer != (-1, -1):
            return []
        
        return [cls()]
    
    @classmethod
    def get_name(cls) -> str:
        return "SkipAction"
    
    def __repr__(self):
        return "SkipAction()"
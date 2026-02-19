import time

from collections import defaultdict

from src.environment.actions import Action, BattleAction
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap, Territory

from src.observers.observer import Observer
from src.observers.player_data import BattleLog, PlayerData

class BattleObserver(Observer):
    """Observer for tracking battle events for experimental analysis."""
    def __init__(self, risk_map: RiskMap, player_datum: list[PlayerData]):
        super().__init__(risk_map, player_datum)

        self.turn_count = 1

    def on_action_taken(self, action: Action, previous_state: GameState, current_state: GameState):
        if previous_state.current_phase == GamePhase.FORTIFY and current_state.current_phase == GamePhase.DRAFT:
            self.turn_count += 1

        if isinstance(action, BattleAction):
            battle_log = BattleLog(
                turn_number=self.turn_count,
                attacker_player_id=previous_state.current_player,
                attacker_territory_id=action.attacker_territory_id,
                attacker_troops=previous_state.territory_troops[action.attacker_territory_id],
                defender_player_id=previous_state.territory_owners[action.defender_territory_id],
                defender_territory_id=action.defender_territory_id,
                defender_troops=previous_state.territory_troops[action.defender_territory_id],
                successful_battle=current_state.current_territory_transfer == (action.attacker_territory_id, action.defender_territory_id)
            )

            self.player_datum[battle_log.attacker_player_id].attacks.append(battle_log)
            self.player_datum[battle_log.defender_player_id].defenses.append(battle_log)
    
    def summarise(self) -> str:
        lines = ["#### Player Battle Statistics ####"]

        # Add player-specific battle summaries
        win_rates = self.get_battle_win_rates()
        average_battles_per_turn = self.get_average_battles_per_turn()
        for player_data in self.player_datum:
            lines.append(f"Player {player_data.player_id} initiated {len(player_data.attacks)} battles with a win rate of {win_rates[player_data.player_id]:.2f} and an average of {average_battles_per_turn[player_data.player_id]:.2f} battles per turn.")
        
        # Add map-specific battle summaries
        lines.append(f"\n#### Map Battle Statistics ####")
        territory_battle_count = self.get_territory_battle_counts()
        most_contested_territories = sorted(territory_battle_count.items(), key=lambda x: x[1], reverse=True)[:5]
        lines.append(f"The top 5 most contested territories were: {', '.join(f'{territory.name} ({count} battles)' for territory, count in most_contested_territories)}.")

        return "\n".join(lines)
    
    def get_battle_win_rates(self) -> list[float]:
        """Calculate the battle win rate for each player based on their recorded attacks and their outcomes."""
        win_rates = []

        for player_data in self.player_datum:
            total_attacks = len(player_data.attacks)
            successful_attacks = sum(1 for attack in player_data.attacks if attack.successful_battle)
            win_rate = successful_attacks / total_attacks if total_attacks > 0 else 0.0
            win_rates.append(win_rate)

        return win_rates

    def get_average_battles_per_turn(self) -> list[float]:
        """Calculate the average number of battles initiated per turn for each player."""
        average_battles_per_turn = []

        for player_data in self.player_datum:
            total_battles = len(player_data.attacks)
            average_battles = total_battles / (player_data.eliminated_turn_count if player_data.eliminated_turn_count else self.turn_count)
            average_battles_per_turn.append(average_battles)

        return average_battles_per_turn
    
    def get_territory_battle_counts(self) -> dict[Territory, int]:
        """Calculate the number of times each territory was targeted in a battle across all players."""
        territory_battle_count = defaultdict(int)

        for player_data in self.player_datum:
            for battle_log in player_data.attacks:
                territory_battle_count[self.risk_map.territories[battle_log.defender_territory_id]] += 1

        return territory_battle_count

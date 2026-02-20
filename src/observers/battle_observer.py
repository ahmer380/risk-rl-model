from tabulate import tabulate

from collections import defaultdict

from src.environment.actions import Action, BattleAction
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap, Territory

from src.observers.observer import Observer
from src.observers.player_telemetry import BattleLog, PlayerTelemetry

class BattleObserver(Observer):
    """Observer for tracking battle events for experimental analysis."""
    def __init__(self, risk_map: RiskMap, player_telemetries: list[PlayerTelemetry]):
        super().__init__(risk_map, player_telemetries)

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

            self.player_telemetries[battle_log.attacker_player_id].attacks.append(battle_log)
            self.player_telemetries[battle_log.defender_player_id].defenses.append(battle_log)
    
    def summarise(self) -> str:
        lines = ["#### Player Battle Statistics ####"]

        # Add player-specific battle summaries
        win_rates = self.get_battle_win_rates()
        average_battles_per_turn = self.get_average_battles_per_turn()
        player_headers = [
            "Player",
            "Battles\ninitiated",
            "Battles\nwon",
            "Win\nrate (%)",
            "Average\nbattles\nper turn"
        ]
        player_rows = []
        for player_telemetry in self.player_telemetries:
            player_row = []
            player_row.append(f"Player {player_telemetry.player_id}")
            player_row.append(len(player_telemetry.attacks))
            player_row.append(sum(1 for attack in player_telemetry.attacks if attack.successful_battle))
            player_row.append(win_rates[player_telemetry.player_id] * 100)
            player_row.append(average_battles_per_turn[player_telemetry.player_id])
            player_rows.append(player_row)
        lines.append(tabulate(player_rows, headers=player_headers, tablefmt="grid", colalign=["center"]*len(player_headers)))
        
        # Add map-specific battle summaries
        lines.append(f"\n#### Map Battle Statistics ####")
        territory_battle_count = self.get_territory_battle_counts()
        map_headers = [
            "Territory",
            "Battles\nas\nattacker",
            "Battles\nas\ndefender"
        ]
        map_rows = []
        for territory, (attacks, defenses) in sorted(territory_battle_count.items(), key=lambda x: (x[1][0], x[0].name), reverse=True):
            map_row = []
            map_row.append(territory.name)
            map_row.append(attacks)
            map_row.append(defenses)
            map_rows.append(map_row)
        lines.append(tabulate(map_rows, headers=map_headers, tablefmt="grid", colalign=["center"]*len(map_headers)))

        return "\n".join(lines)
    
    def get_battle_win_rates(self) -> list[float]:
        """Calculate the battle win rate for each player based on their recorded attacks and their outcomes."""
        win_rates = []

        for player_telemetry in self.player_telemetries:
            total_attacks = len(player_telemetry.attacks)
            successful_attacks = sum(1 for attack in player_telemetry.attacks if attack.successful_battle)
            win_rate = successful_attacks / total_attacks if total_attacks > 0 else 0.0
            win_rates.append(win_rate)

        return win_rates

    def get_average_battles_per_turn(self) -> list[float]:
        """Calculate the average number of battles initiated per turn for each player."""
        average_battles_per_turn = []

        for player_telemetry in self.player_telemetries:
            total_battles = len(player_telemetry.attacks)
            average_battles = total_battles / (player_telemetry.eliminated_turn_count if player_telemetry.eliminated_turn_count else self.turn_count)
            average_battles_per_turn.append(average_battles)

        return average_battles_per_turn
    
    def get_territory_battle_counts(self) -> dict[Territory, list[int]]:
        """Calculate the number of times each territory attacked, or was attacked in a battle across all players."""
        territory_battle_counts: dict[Territory, list[int]] = defaultdict(lambda: [0, 0])  # [attacks, defenses]

        for player_telemetry in self.player_telemetries:
            for battle_log in player_telemetry.attacks:
                territory_battle_counts[self.risk_map.territories[battle_log.attacker_territory_id]][0] += 1
                territory_battle_counts[self.risk_map.territories[battle_log.defender_territory_id]][1] += 1

        return territory_battle_counts

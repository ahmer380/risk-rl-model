from typing import Self

from tabulate import tabulate

from collections import defaultdict

from src.environment.actions import Action, BattleAction
from src.environment.game_state import GameState
from src.environment.map import Territory

from src.observers.observer import Observer
from src.observers.player_telemetry import PlayerTelemetry, BattleLog

class BattleObserver(Observer):
    """Observer for tracking battle events for experimental analysis."""
    def on_action_taken(self, action: Action, previous_state: GameState, current_state: GameState):
        if isinstance(action, BattleAction):
            battle_log = BattleLog(
                turn_number=self.core_observer.turn_count,
                attacker_player_id=previous_state.current_player,
                attacker_territory_id=action.attacker_territory_id,
                attacker_troops=previous_state.territory_troops[action.attacker_territory_id],
                defender_player_id=previous_state.territory_owners[action.defender_territory_id],
                defender_territory_id=action.defender_territory_id,
                defender_troops=previous_state.territory_troops[action.defender_territory_id],
                successful_battle=current_state.current_territory_transfer == (action.attacker_territory_id, action.defender_territory_id)
            )

            self.core_observer.player_telemetries[battle_log.attacker_player_id].attacks.append(battle_log)
            self.core_observer.player_telemetries[battle_log.defender_player_id].defenses.append(battle_log)
    
    def summarise_game(self) -> str:
        lines = ["#### Battle Observations ####"]

        # Add player-specific battle summaries
        lines.append(f"\n---- Player Battle Statistics ----")
        player_headers = [
            "Player",
            "Battles\ninitiated",
            "Battles\nwon",
            "Win\nrate (%)",
            "Average\nbattles\nper turn",
            "Average\nbattle\ndifferential"
        ]
        player_rows = []
        for player_telemetry in self.core_observer.player_telemetries:
            player_row = []
            player_row.append(f"Player {player_telemetry.player_id}")
            player_row.append(len(player_telemetry.attacks))
            player_row.append(self.get_total_successful_battles(player_telemetry))
            player_row.append(self.get_battle_win_rate(player_telemetry) * 100)
            player_row.append(self.get_average_battles_per_turn(player_telemetry))
            player_row.append(self.get_average_battle_differential(player_telemetry))
            player_rows.append(player_row)
        lines.append(tabulate(player_rows, headers=player_headers, tablefmt="grid", colalign=["center"]*len(player_headers)))
        
        # Add map-specific battle summaries
        lines.append(f"\n---- Map Battle Statistics ----")
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
    
    def get_total_successful_battles(self, player_telemetry: PlayerTelemetry) -> int:
        """Return the total number of successful battles for a given player."""
        return sum(1 for attack in player_telemetry.attacks if attack.successful_battle)

    def get_battle_win_rate(self, player_telemetry: PlayerTelemetry) -> float:
        """Calculate the battle win rate for a given player."""
        return self.get_total_successful_battles(player_telemetry) / len(player_telemetry.attacks) if player_telemetry.attacks else 0.0

    def get_average_battles_per_turn(self, player_telemetry: PlayerTelemetry) -> float:
        """Calculate the average number of battles initiated per turn for a given player."""
        return len(player_telemetry.attacks) / self.core_observer.get_player_turn_count(player_telemetry) if self.core_observer.get_player_turn_count(player_telemetry) > 0 else 0.0
    
    def get_total_battle_differential(self, player_telemetry: PlayerTelemetry) -> int:
        return sum(attack.attacker_troops - attack.defender_troops for attack in player_telemetry.attacks)
    
    def get_average_battle_differential(self, player_telemetry: PlayerTelemetry) -> float:
        return self.get_total_battle_differential(player_telemetry) / len(player_telemetry.attacks) if player_telemetry.attacks else 0.0
    
    def get_territory_battle_counts(self) -> dict[Territory, list[int]]:
        """Calculate the number of times each territory attacked, or was attacked in a battle across all players."""
        territory_battle_counts: dict[Territory, list[int]] = defaultdict(lambda: [0, 0])  # [attacks, defenses]

        for player_telemetry in self.core_observer.player_telemetries:
            for battle_log in player_telemetry.attacks:
                territory_battle_counts[self.core_observer.risk_map.territories[battle_log.attacker_territory_id]][0] += 1
                territory_battle_counts[self.core_observer.risk_map.territories[battle_log.defender_territory_id]][1] += 1

        return territory_battle_counts
    
    """Class methods for collecting and summarising aggregate outcome data for experimental anlaysis """
    
    @classmethod
    def summarise_simulation(cls, observers: list[Self]) -> str:
        lines = ["#### Battle Simulation Summary ####"]

        # Add player-specific battle summaries
        lines.append(f"\n---- Player Battle Statistics ----")
        player_headers = ["Player", "Battle\nwin\nrate (%)", "Average\nbattles\nper turn", "Average\nbattle\ndifferential"]
        lines.append(tabulate(cls.get_player_battle_statistics(observers), headers=player_headers, tablefmt="grid", colalign=["center"]*len(player_headers)))
        
        return "\n".join(lines)

    @classmethod
    def get_player_battle_statistics(cls, observers: list[Self]) -> list[list]:
        """Return list of [player_id, battle win rate, average battles per turn, average battle differential] for each player."""
        rows = []

        for player_id in range(len(observers[0].core_observer.player_telemetries)):
            total_battles, total_successful_battles, total_battle_differential, total_turns = 0, 0, 0, 0

            for observer in observers:
                player_telemetry = observer.core_observer.player_telemetries[player_id]
                total_battles += len(player_telemetry.attacks)
                total_successful_battles += observer.get_total_successful_battles(player_telemetry)
                total_battle_differential += observer.get_total_battle_differential(player_telemetry)
                total_turns += observer.core_observer.get_player_turn_count(player_telemetry)
            
            rows.append([
                f"Player {player_id}",
                f"{(total_successful_battles / total_battles * 100 if total_battles > 0 else 0):.2f}%",
                f"{(total_battles / total_turns if total_turns > 0 else 0):.2f}",
                f"{(total_battle_differential / total_battles if total_battles > 0 else 0):.2f}"
            ])

        return rows

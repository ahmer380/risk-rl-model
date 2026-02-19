import time

from collections import defaultdict

from src.environment.actions import Action, BattleAction
from src.environment.game_state import GameState, GamePhase
from src.environment.map import RiskMap, Territory

class BattleLog:
    def __init__(
        self,
        turn_number: int,
        attacker_player_id: int, 
        attacker_territory_id: int,
        attacker_troops: int,
        defender_player_id: int, 
        defender_territory_id: int, 
        defender_troops: int, 
        successful_battle: bool
    ):
        self.turn_number = turn_number
        self.attacker_player_id = attacker_player_id
        self.attacker_territory_id = attacker_territory_id
        self.defender_player_id = defender_player_id
        self.defender_territory_id = defender_territory_id
        self.attacker_troops = attacker_troops
        self.defender_troops = defender_troops
        self.successful_battle = successful_battle

class PlayerObserver:
    """Observer for tracking individual player actions and outcomes for a single Risk game."""
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.attacks: list[BattleLog] = [] # log of battles initiated by the player
        self.defenses: list[BattleLog] = [] # log of battles initiated to the player, and outcome (true = failed defense)
        self.eliminated_turn_count: int = None # turn number when the player was eliminated or None if still in the game

class GameObserver:
    """Observer for tracking events and player actions for a single Risk game.
    The GameObserver is NOT responsible for influencing the environment state nor agent decisions/rewards."""
    def __init__(self, risk_map: RiskMap, num_players: int):
        self.risk_map = risk_map
        self.player_observers = [PlayerObserver(i) for i in range(num_players)]
        self.action_count = 0
        self.turn_count = 1
        self.terminal_state: GameState = None # Store the terminal state of the game for post-game analysis
        self.running_time: float = None # Total time taken for the episode
    
    def on_game_start(self):
        self.running_time = time.time()

    def on_action_taken(self, action: Action, previous_state: GameState, current_state: GameState):
        self.action_count += 1

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

            self.player_observers[battle_log.attacker_player_id].attacks.append(battle_log)
            self.player_observers[battle_log.defender_player_id].defenses.append(battle_log)
    
    def on_game_end(self, terminal_state: GameState):
        self.terminal_state = terminal_state
        self.running_time = time.time() - self.running_time
    
    def get_battle_win_rates(self) -> list[float]:
        """Calculate the battle win rate for each player based on their recorded attacks and their outcomes."""
        win_rates = []

        for player_observer in self.player_observers:
            total_attacks = len(player_observer.attacks)
            successful_attacks = sum(1 for attack in player_observer.attacks if attack.successful_battle)
            win_rate = successful_attacks / total_attacks if total_attacks > 0 else 0.0
            win_rates.append(win_rate)

        return win_rates

    def get_average_battles_per_turn(self) -> list[float]:
        """Calculate the average number of battles initiated per turn for each player."""
        average_battles_per_turn = []

        for player_observer in self.player_observers:
            total_battles = len(player_observer.attacks)
            average_battles = total_battles / (player_observer.eliminated_turn_count if player_observer.eliminated_turn_count else self.turn_count)
            average_battles_per_turn.append(average_battles)

        return average_battles_per_turn
    
    def get_territory_battle_counts(self) -> dict[Territory, int]:
        """Calculate the number of times each territory was targeted in a battle across all players."""
        territory_battle_count = defaultdict(int)

        for player_observer in self.player_observers:
            for battle_log in player_observer.attacks:
                territory_battle_count[self.risk_map.territories[battle_log.defender_territory_id]] += 1

        return territory_battle_count
    
    def summarise(self) -> str:
        lines = []
        lines.append(f"Episode ended after {self.running_time:.2f} seconds, {self.action_count} actions and {self.turn_count} turns.")

        lines.append(f"\n#### Final Game State ####")
        lines.append(f"Winner: Player {self.terminal_state.get_winner()}" if self.terminal_state.is_terminal_state() else "No winner")
        lines.append(f"{self.terminal_state}")

        # Add player-specific summaries
        lines.append(f"\n#### Player Statistics ####")
        win_rates = self.get_battle_win_rates()
        average_battles_per_turn = self.get_average_battles_per_turn()
        for player_observer in self.player_observers:
            lines.append(f"Player {player_observer.player_id} initiated {len(player_observer.attacks)} battles with a win rate of {win_rates[player_observer.player_id]:.2f} and an average of {average_battles_per_turn[player_observer.player_id]:.2f} battles per turn.")
        
        # Add map-specific summaries
        lines.append(f"\n#### Map Statistics ####")
        territory_battle_count = self.get_territory_battle_counts()
        most_contested_territories = sorted(territory_battle_count.items(), key=lambda x: x[1], reverse=True)[:5]
        lines.append(f"The top 5 most contested territories were: {', '.join(f'{territory.name} ({count} battles)' for territory, count in most_contested_territories)}.")

        return "\n".join(lines)

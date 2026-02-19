from src.environment.actions import DeployAction, TradeAction, BattleAction, TransferAction, FortifyAction, SkipAction

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

class PlayerData(): # TODO: Find better name for this class
    """Entity that stores player data during a game, to be read and written by observers."""
    def __init__(self, player_id: int):
        self.player_id = player_id

        # attributes to be used by the BattleObserver
        self.attacks: list[BattleLog] = [] # log of battles initiated by the player
        self.defenses: list[BattleLog] = [] # log of battles initiated to the player, and outcome (true = failed defense)
        self.eliminated_turn_count: int = None # turn number when the player was eliminated or None if still in the game

        # attributes to be used by the TemporalObserver
        self.action_counts_per_turn = {
            DeployAction.get_name(): [],
            TradeAction.get_name(): [],
            BattleAction.get_name(): [],
            TransferAction.get_name(): [],
            FortifyAction.get_name(): [],
            SkipAction.get_name(): []
        } #key=action_type, value=list of action counts indexed per turn
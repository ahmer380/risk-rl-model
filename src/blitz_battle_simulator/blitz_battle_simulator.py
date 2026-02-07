import csv
import random

class BlitzBattleSimulator:
    def __init__(self):
        # key = (attacker_troops, defender_troops), value = {key = (remaining_attacker_troops, remaining_defender_troops), value = probability}
        self.blitz_probability_matrix: dict[tuple[int, int], dict[tuple[int, int], float]] = {}

        with open("src/blitz_battle_simulator/blitz_probability_matrix.csv", "r") as file:
            reader = csv.reader(file)
            headers = next(reader)
            self.dimension = int(headers[1][1:-1].split("/")[0])

            for row in reader:
                attacker_troops, defender_troops = map(int, row[0][1:-1].split("/"))
                self.blitz_probability_matrix[(attacker_troops, defender_troops)] = {}
                for i, battle_outcome in enumerate(headers[1:-1]):
                    remaining_attacker_troops, remaining_defender_troops = map(int, battle_outcome[1:-1].split("/"))
                    if attacker_troops >= remaining_attacker_troops and defender_troops >= remaining_defender_troops:
                        self.blitz_probability_matrix[(attacker_troops, defender_troops)][(remaining_attacker_troops, remaining_defender_troops)] = float(row[i+1])
    
    def simulate_battle(self, attacker_troops: int, defender_troops: int) -> tuple[int, int]:
        def interpolated_battle(A: int, D: int) -> tuple[int, int]:
            r = random.random()
            cumulative_probability = 0.0

            for outcome, probability in self.blitz_probability_matrix[(A, D)].items():
                cumulative_probability += probability
                if r < cumulative_probability:
                    return outcome
            
            return max(self.blitz_probability_matrix[(A, D)].keys(), key=lambda outcome: self.blitz_probability_matrix[(A, D)][outcome]) # fallback to most likely outcome in unlikely event of floating point precision issues
        
        if attacker_troops <= self.dimension and defender_troops <= self.dimension:
            return interpolated_battle(attacker_troops, defender_troops)
         
        # Otherwise, we are extrapolating from the blitz probability matrix... TODO: Make more accurate!
        scale = max(attacker_troops, defender_troops) / self.dimension
        A, D = max(1, round(attacker_troops / scale)), max(1, round(defender_troops / scale))
        remaining_attacker_troops, remaining_defender_troops = interpolated_battle(A, D)

        if remaining_attacker_troops == 1:
            return (1, round(remaining_defender_troops * scale)) # Do not upscale attacker troop if they lose

        return (round(remaining_attacker_troops * scale), round(remaining_defender_troops * scale))

    def __str__(self):
        lines = []
        lines.append(f"{self.dimension} X {self.dimension} BlitzProbabilityMatrix:")
        for battle, outcome_probabilities in self.blitz_probability_matrix.items():
            outcomes = ", ".join([f"{str(outcome).replace(' ', '')}={probability}" for outcome, probability in outcome_probabilities.items()])
            lines.append(f"{str(battle).replace(' ', '')}: {outcomes}")
        
        return "\n".join(lines)

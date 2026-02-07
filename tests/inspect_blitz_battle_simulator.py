from collections import Counter

from src.blitz_battle_simulator.blitz_battle_simulator import BlitzBattleSimulator

def run_battle_simulation_multiple_times(attacker_troops: int, defender_troops: int):
    simulator = BlitzBattleSimulator()
    outcome_counter = Counter(simulator.simulate_battle(attacker_troops, defender_troops) for _ in range(1000))
    
    print(f"Simulated 1000 battles with {attacker_troops} attackers and {defender_troops} defenders:")
    for (remaining_attacker_troops, remaining_defender_troops), count in outcome_counter.items():
        print(f"{remaining_attacker_troops} remaining attacker(s) and {remaining_defender_troops} remaining defender(s): {count} times ({count/1000:.2%})")
    print(f"Attacker win rate: {sum(count for (_, defender), count in outcome_counter.items() if defender == 0) / 1000:.2%} \n")

# No assertions here, just want to eyeball simulation results such that they look okay
run_battle_simulation_multiple_times(10, 1)
run_battle_simulation_multiple_times(100, 1)
run_battle_simulation_multiple_times(5, 10)
run_battle_simulation_multiple_times(11, 21)
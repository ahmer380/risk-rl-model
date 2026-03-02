import time

from collections import Counter

from src.blitz_battle_simulator.blitz_battle_simulator import BlitzBattleSimulator

def run_battle_simulation_multiple_times(attacker_troops: int, defender_troops: int):
    start_time = time.time()
    outcome_counter = Counter(simulator.simulate_battle(attacker_troops, defender_troops) for _ in range(1000))
    end_time = time.time()
    
    print(f"Simulated 1000 battles with {attacker_troops} attackers and {defender_troops} defenders:")
    for (remaining_attacker_troops, remaining_defender_troops), count in outcome_counter.items():
        print(f"{remaining_attacker_troops} remaining attacker(s) and {remaining_defender_troops} remaining defender(s): {count} times ({count/1000:.2%})")
    print(f"Attacker win rate: {sum(count for (_, defender), count in outcome_counter.items() if defender == 0) / 1000:.2%}")
    print(f"Simulation took {end_time - start_time:.2f} seconds, average time per battle: {(end_time - start_time) / 1000:.4f} seconds\n")

# Load BlitzBattleSimulator, this may take some time!
start_time = time.time()
simulator = BlitzBattleSimulator(100)
end_time = time.time()
print(f"BlitzBattleSimulator for {simulator.dimension}X{simulator.dimension} matrix loaded in {end_time - start_time:.2f} seconds\n")

# No assertions here, just want to eyeball simulation results such that they look okay
run_battle_simulation_multiple_times(10, 1)
run_battle_simulation_multiple_times(100, 1)
run_battle_simulation_multiple_times(5, 10)
run_battle_simulation_multiple_times(11, 21)
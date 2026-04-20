# Risk RL Model

This repository contains the experimental framework developed for my research project investigating how reinforcement learning agents develop strategic behaviour in a Risk-inspired board game environment. It serves as a controlled testbed for analysing how map topology, player count, and opponent composition influence emergent strategy. The framework integrates a Proximal Policy Optimisation (PPO) training pipeline, rule-based baseline agents, and a modular simulation and telemetry system, enabling reproducible experiments and systematic evaluation of learned policies.

This repository includes:
- A PPO training pipeline for an RL Risk agent
- Rule-based baseline agents for comparison
- Simulation runners for repeatable experiments
- Observer modules that collect telemetry and summary statistics

## Project Layout (some key files/folders)

- `src/train/train.py`: PPO training entry point
- `src/train/ppo.py`: PPO model configuration, training, saving, loading
- `src/runners/simulation_runner.py`: Multi-episode simulation loop
- `src/agents/agent.py`: Available baseline agents (`RandomAgent`, `CommunistAgent`, `CapitalistAgent`)
- `src/utils/k_clique_generator.py`: Utility for automatically generating k-clique map JSON definitions
- `src/experiments/`: Pre-defined experiment scripts (`mini_map.py`, `classic.py`, `experiment1.py`, `experiment2.py`, `experiment3.py`)
- `src/observers/`: Telemetry observers (battle, outcome, deploy, action counts)
- `maps/`: Pre-configured map definitions (`mini.json`, `classic.json`)

## Setup

### Step 0: Ensure Python and pip are installed

```bash
python --version
pip --version
```

### Step 1: Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

## Train an RL Agent with PPO

Training is implemented in `src/train/train.py` and utilises `RiskPPO` from `src/train/ppo.py`.


Pass custom map and player count:

```bash
python src/train/train.py --map_name classic --num_players 4
```

Supported executable parameters:
- `--map_name`: map name to train on (`mini`, `classic`, or a value starting with `clique`)
- `--num_players`: number of players in the training environment
- `--clique_size`: required when using a clique-generated map
- `--clique_density`: required when using a clique-generated map (`min` or `max`)

Example for clique map training:

```bash
python src/train/train.py --map_name clique --num_players 2 --clique_size 8 --clique_density min
```

## Run Pre-Defined Experiments

The included example experiment is `src/experiments/mini_map.py`.

What it does:
- loads map: `maps/mini.json`
- uses agents: `CommunistAgent` vs `CommunistAgent`
- runs two scenarios (fixed turn order and shuffled turn order)
- runs `1000` simulation episodes per scenario
- tracks telemetry with `OutcomeObserver` and `BattleObserver`

Run it:

```bash
python src/experiments/mini_map.py
```

The script prints aggregate simulation summaries to the console.

Other predefined experiments:
- `python src/experiments/classic.py`
- `python src/experiments/experiment1.py`
- `python src/experiments/experiment2.py`
- `python src/experiments/experiment3.py`

## Define Your Own Experiment!

You can create your own file in `src/experiments/` by selecting:
- Agent composition
- Map to play on
- Number of simulations (episodes)
- Observers to track telemetry data

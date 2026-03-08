# Risk RL Model

Reinforcement learning and simulation framework for a Risk-like strategy environment.

This repository includes:
- A PPO training pipeline for a RL Risk agent
- Rule-based baseline agents for comparison
- Simulation runners for repeatable experiments
- Observer modules that collect telemetry and summary statistics

## Project Layout (some key files/folders)

- `src/train/train.py`: PPO training entry point
- `src/train/ppo.py`: PPO model configuration, training, saving, loading
- `src/experiments/mini_map_2_player.py`: exemplar experiment on the mini map with 2 players
- `src/runners/simulation_runner.py`: multi-episode simulation loop
- `src/agents/agent.py`: available baseline agents
- `src/observers/`: telemetry observers (battle, outcome, trajectory, action counts)
- `maps/`: map definitions (`mini.json`, `classic.json`)

## Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

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
- `--map_name`: map name to train on
- `--num_players`: number of players in the training environment

## Run Pre-Defined Experiments

The included example experiment is `src/experiments/mini_map_2_player.py`.

What it does:
- loads map: `maps/mini.json`
- uses agents: `AdvantageAttackAgent(0)` vs `RandomAgent(1)`
- runs `100` simulation episodes
- tracks telemetry with `OutcomeObserver` and `BattleObserver`

Run it:

```bash
python src/experiments/mini_map_2_player.py
```

The script prints aggregate simulation summaries to the console.

## Define Your Own Experiment!

You can create your own file in `src/experiments/` by selecting:
- Agent composition
- Map to play on
- Number of simulations (episodes)
- Observers to track telemetry data
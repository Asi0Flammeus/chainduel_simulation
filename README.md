# Chain Duel Simulation

A Python simulation model for analyzing AI strategies in Chain Duel, inspired by [Chain Duel Online](https://chainduel.net/).

## Introduction

This project simulates snake-like AI duels where two agents compete for food while avoiding collisions. The simulation helps analyze different competitive strategies and their effectiveness in a controlled environment.

## Setup (Ubuntu)

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Requirements (`requirements.txt`):
```
tk
tqdm
```

## Usage

Run the simulation:
```bash
python main.py
```

Choose from three modes:
- Player vs AI
- AI vs AI
- Simulation (batch runs with statistics)

Simulation results are saved in `simulations/sim_TIMESTAMP/`:
- `results.txt`: Game-by-game data
- `stats.txt`: Aggregated statistics

## Project Structure

```
├── main.py          # Main entry point
├── src/
│   ├── core/        # Game mechanics
│   ├── strategies/  # AI implementations
│   ├── ui/         # Game interface
│   └── simulation/ # Batch simulation
```

## TODO

### Scoring System
- [ ] Evaluate point deduction on first food collection
- [ ] Implement competitive scoring mechanics
- [ ] Add multiplication factors based on snake length

### AI Strategy Improvements
- [ ] Implement direct path to first food (Player 1)
- [ ] Add hairpin maneuver for first food (Player 2)
- [ ] Develop minimal avoidance with food seeking
- [ ] Food-unreachable behaviors:
  - [ ] Center positioning
  - [ ] Board half switching
  - [ ] Quadrant selection (based on food history)

## License

MIT License - Feel free to use this code for any purpose while maintaining the license notice.

## Reference

Based on the Chain Duel game: https://chainduel.net/

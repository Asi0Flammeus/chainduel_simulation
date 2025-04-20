# Chain Duel Simulation

A Python simulation model for analyzing AI strategies in Chain Duel, inspired by [Chain Duel Online](https://chainduel.net/).

## Introduction

This project offers three modes for snake-like duels:
- Interactive mode with grid display:
  - Play against AI (use arrow keys)
  - Watch two AIs compete
- Simulation mode for batch analysis

## Setup (Ubuntu)

```bash
# Create and activate virtual environment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Start the game:
```bash
python main.py
```

### Interactive Modes
- **Player vs AI**: Control green snake with arrow keys while AI controls orange
- **AI vs AI**: Watch two AI strategies compete in real-time
- Controls: R to restart, ESC to quit

### Simulation Mode
Runs multiple games without visualization for statistical analysis. Results saved in `simulations/sim_TIMESTAMP/`:
- `results.txt`: Detailed game data
- `stats.txt`: Performance metrics

### Batch Analysis
1. Run full batch simulation across all strategies and cases:
   ```bash
   python run_batch_simulations.py
   ```
   This generates `batch_results.csv` and `STRATEGIES_AND_CASES.md` in the project root.
2. Analyze and visualize the results:
   ```bash
   python analyze_results.py
   ```
   Outputs are saved under `analysis_outputs/`:
   - `RESULTS_SUMMARY.md`: Markdown report with
     - Overall average win‑rate table and bar chart
     - Per‑case win‑rate matrices and heatmaps
     - Strategy win‑rate comparison across the 4 initial cases (table & line chart)
   - PNG charts:
     - `overall_avg_win_rate.png`
     - `heatmap_<case>.png` (one per case)
     - `comparison_win_rate_cases.png` (strategy vs cases)

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

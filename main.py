# main.py
import tkinter as tk
from src.common.constants import GameConfig
from src.common.enums import GameMode
from src.ui.setup import get_game_settings
from src.ui.game_canvas import GameCanvas
from src.utils.debug import DebugLogger
from src.simulation.runner import ScenarioSimulationRunner
from src.strategies.ai import (SimpleFoodSeekingStrategy, AdaptiveSeekingStrategy,
                          AggressiveStrategy, NoisyAdaptiveStrategy)  # Import strategies
import csv
import os
from datetime import datetime

def setup_game_window(root: tk.Tk, config: GameConfig) -> None:
    """Setup the main game window and center it on screen."""
    root.title("Chain Duel")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - config.WINDOW_WIDTH) // 2
    y = (screen_height - config.WINDOW_HEIGHT) // 2
    root.geometry(f'{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}')

def create_controls_label(root: tk.Tk, mode: GameMode, config: GameConfig) -> None:
    """Create and display the controls help text."""
    controls_text = "Controls: Arrow Keys (Green) | R: Restart | ESC: Quit" if mode == GameMode.PLAYER_VS_AI else "Controls: R: Restart | ESC: Quit"
    controls = tk.Label(
        root,
        text=controls_text,
        bg=config.BACKGROUND_COLOR,
        fg=config.TEXT_COLOR
    )
    controls.pack(side='bottom')

def run_interactive_mode(mode: GameMode, strategy1, strategy2, debug: DebugLogger) -> None:
    """Run the game in interactive mode (with visual display)."""
    root = tk.Tk()
    config = GameConfig()
    
    setup_game_window(root, config)
    
    # Create and setup game canvas
    game = GameCanvas(root, mode, config, strategy1, strategy2, debug)
    game.pack(expand=True, fill='both')
    create_controls_label(root, mode, config)
    
    # Handle window closing
    def on_closing():
        debug.log("Game closing")
        debug.close()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    debug.log("Starting main game loop")
    root.mainloop()

def run_simulation_mode(strategy1, strategy2, num_runs: int) -> None:
    """Run the game in simulation mode (batch processing)."""
    print("\nStarting simulation...")
    runner = ScenarioSimulationRunner(strategy1, strategy2, num_runs)
    runner.run()

def run_game_mode(mode: GameMode, strategy1, strategy2, debug_enabled: bool, num_runs: int = None) -> None:
    """Run the game in the specified mode with given settings."""
    if mode == GameMode.SIMULATION:
        run_simulation_mode(strategy1, strategy2, num_runs)
    else:
        debug = DebugLogger(debug_enabled)
        debug.log("Game started")
        run_interactive_mode(mode, strategy1, strategy2, debug)

def run_full_simulation(num_runs: int, output_dir: str) -> None:
    """Run simulations for all strategy combinations and save results to CSV."""

    strategies = {
        "Simple": SimpleFoodSeekingStrategy,
        "Adaptive": AdaptiveSeekingStrategy,
        "Aggressive": AggressiveStrategy,
        "Noisy": NoisyAdaptiveStrategy
    }

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(output_dir, f"full_sim_results_{timestamp}.csv")

    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Modified header to include results per position
        csv_writer.writerow(["Strategy1", "Strategy2", "Position", "Wins1", "Wins2", "AvgScore1", "AvgScore2", "MaxLength1", "MaxLength2", "AvgGameLength"])

        for name1, strategy1_class in strategies.items():
            for name2, strategy2_class in strategies.items():
                print(f"\nRunning simulations: {name1} vs {name2}")
                strategy1 = strategy1_class()
                strategy2 = strategy2_class()
                runner = ScenarioSimulationRunner(strategy1, strategy2, num_runs)
                runner.run()

                # Iterate through each starting position and extract stats
                for position, pos_stats in runner.stats['position_stats'].items():
                    wins1 = pos_stats['wins1']
                    wins2 = pos_stats['wins2']
                    avg_score1 = sum(pos_stats['avg_score1']) / len(pos_stats['avg_score1']) if pos_stats['avg_score1'] else 0
                    avg_score2 = sum(pos_stats['avg_score2']) / len(pos_stats['avg_score2']) if pos_stats['avg_score2'] else 0

                    # Extract overall max lengths and game lengths (these are not position-specific in the current runner)
                    max_length1 = max(runner.stats['max_length1']) if runner.stats['max_length1'] else 0
                    max_length2 = max(runner.stats['max_length2']) if runner.stats['max_length2'] else 0
                    avg_game_length = sum(runner.stats['game_lengths']) / len(runner.stats['game_lengths']) if runner.stats['game_lengths'] else 0

                    # Write results to CSV, including the position
                    csv_writer.writerow([name1, name2, position, wins1, wins2, avg_score1, avg_score2, max_length1, max_length2, avg_game_length])
                    csvfile.flush()  # Ensure data is written immediately

    print(f"\nFull simulation results saved to: {csv_filename}")

def main():
    settings = get_game_settings()

    if settings and settings[0] == "full_simulation":  # Check for full simulation mode
        _, num_runs, output_dir = settings  # Unpack settings
        run_full_simulation(int(num_runs), output_dir)
    elif len(settings) == 5:  # Simulation mode
        mode, strategy1, strategy2, _, num_runs = settings
        run_game_mode(mode, strategy1, strategy2, False, num_runs)
    else:  # Interactive modes
        mode, strategy1, strategy2, enable_debug = settings
        run_game_mode(mode, strategy1, strategy2, enable_debug)

if __name__ == "__main__":
    main()


# main.py
import tkinter as tk
from constants import GameConfig
from enums import GameMode
from setup import get_game_settings
from game_canvas import GameCanvas
from debug import DebugLogger
from runner import SimulationRunner

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
    runner = SimulationRunner(strategy1, strategy2, num_runs)
    runner.run()

def run_game_mode(mode: GameMode, strategy1, strategy2, debug_enabled: bool, num_runs: int = None) -> None:
    """Run the game in the specified mode with given settings."""
    if mode == GameMode.SIMULATION:
        run_simulation_mode(strategy1, strategy2, num_runs)
    else:
        debug = DebugLogger(debug_enabled)
        debug.log("Game started")
        run_interactive_mode(mode, strategy1, strategy2, debug)

def main():
    settings = get_game_settings()
    
    if len(settings) == 5:  # Simulation mode
        mode, strategy1, strategy2, _, num_runs = settings
        run_game_mode(mode, strategy1, strategy2, False, num_runs)
    else:  # Interactive modes
        mode, strategy1, strategy2, enable_debug = settings
        run_game_mode(mode, strategy1, strategy2, enable_debug)

if __name__ == "__main__":
    main()

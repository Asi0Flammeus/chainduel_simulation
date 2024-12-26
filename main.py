import tkinter as tk
from src.common.constants import GameConfig
from src.common.enums import GameMode
from src.ui.setup import get_game_settings
from src.ui.game_canvas import GameCanvas
from src.utils.debug import DebugLogger
from src.simulation.runner import SimulationRunner

def setup_game_window(root: tk.Tk, config: GameConfig) -> None:
    root.title("Snake Game")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - config.WINDOW_WIDTH) // 2
    y = (screen_height - config.WINDOW_HEIGHT) // 2
    root.geometry(f'{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}')

def create_controls_label(root: tk.Tk, mode: GameMode, config: GameConfig) -> None:
    controls_text = "Controls: Arrow Keys (Green) | R: Restart | ESC: Quit" if mode == GameMode.PLAYER_VS_AI else "Controls: R: Restart | ESC: Quit"
    controls = tk.Label(root, text=controls_text, bg=config.BACKGROUND_COLOR, fg=config.TEXT_COLOR)
    controls.pack(side='bottom')

def run_game_mode(mode: GameMode, strategy1, strategy2, debug_enabled: bool, num_runs: int = None) -> None:
    if mode == GameMode.SIMULATION:
        print("\nStarting simulation...")
        runner = SimulationRunner(strategy1, strategy2, num_runs)
        runner.run_simulation()
        return

    debug = DebugLogger(debug_enabled)
    debug.log("Game started")
    root = tk.Tk()
    config = GameConfig()
    setup_game_window(root, config)
    game = GameCanvas(root, mode, config, strategy1, strategy2, debug)
    game.pack(expand=True, fill='both')
    create_controls_label(root, mode, config)
    
    def on_closing():
        debug.log("Game closing")
        debug.close()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    debug.log("Starting main game loop")
    root.mainloop()

def main():
    settings = get_game_settings()
    if len(settings) == 5:
        mode, strategy1, strategy2, _, num_runs = settings
        run_game_mode(mode, strategy1, strategy2, False, num_runs)
    else:
        mode, strategy1, strategy2, enable_debug = settings
        run_game_mode(mode, strategy1, strategy2, enable_debug)

if __name__ == "__main__":
    main()

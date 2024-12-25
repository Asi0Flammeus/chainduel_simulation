import tkinter as tk
from src.common.constants import GameConfig
from src.common.enums import GameMode
from src.ui.setup import get_game_settings
from src.ui.game_canvas import GameCanvas

def main():
    # Get game settings
    mode, strategy1, strategy2 = get_game_settings()
    
    # Create window
    root = tk.Tk()
    root.title("Snake Game")
    
    # Configure game
    config = GameConfig()
    
    # Center window on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - config.WINDOW_WIDTH) // 2
    y = (screen_height - config.WINDOW_HEIGHT) // 2
    root.geometry(f'{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}')
    
    # Create game instance with debug mode
    # Set enable_debug=True to enable logging
    game = GameCanvas(root, mode, config, strategy1, strategy2)
    game.pack(expand=True, fill='both')
    
    # Add control instructions
    if mode == GameMode.PLAYER_VS_AI:
        controls_text = "Controls: Arrow Keys (Green) | R: Restart | ESC: Quit"
    else:
        controls_text = "Controls: R: Restart | ESC: Quit"
    
    controls = tk.Label(
        root,
        text=controls_text,
        bg=config.BACKGROUND_COLOR,
        fg=config.TEXT_COLOR
    )
    controls.pack(side='bottom')
    
    def on_closing():
        game.debug.close()  # Close debug log file
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

from typing import Tuple, Optional, Dict, Type
import inspect
from ..common.enums import GameMode
from ..strategies.base import SnakeStrategy
from ..strategies import ai as ai_module

def get_available_strategies() -> Dict[str, Type[SnakeStrategy]]:
    """Dynamically find all available strategy classes in the ai module."""
    strategies = {}
    for name, obj in inspect.getmembers(ai_module):
        if (inspect.isclass(obj) 
            and issubclass(obj, SnakeStrategy) 
            and obj != SnakeStrategy
            and obj.__module__ == ai_module.__name__):
            # Convert class name to display name (e.g., AggressiveStrategy -> Aggressive)
            display_name = name.replace('Strategy', '')
            strategies[display_name] = obj
    return strategies

def get_game_settings() -> Tuple[GameMode, Optional[SnakeStrategy], Optional[SnakeStrategy], bool]:
    """Get game settings including mode and AI strategies."""
    print("\nWelcome to Snake Game!")
    
    # Get debug mode setting
    while True:
        debug_choice = input("\nEnable debug mode? (y/n): ").lower()
        if debug_choice in ['y', 'n']:
            enable_debug = debug_choice == 'y'
            break
        print("Invalid choice. Please enter 'y' or 'n'.")
    
    # Get game mode
    print("\nSelect Game Mode:")
    print("1. Player vs AI")
    print("2. AI vs AI")
    
    while True:
        try:
            mode_choice = int(input("Enter your choice (1-2): "))
            if 1 <= mode_choice <= len(GameMode):
                mode = list(GameMode)[mode_choice-1]
                break
            print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Get available strategies
    strategies = get_available_strategies()
    strategy_list = list(strategies.items())
    
    def get_strategy_choice(player_num: int) -> SnakeStrategy:
        """Get strategy choice for a player."""
        print(f"\nAvailable strategies for AI {player_num}:")
        for i, (name, _) in enumerate(strategy_list, 1):
            print(f"{i}. {name} Strategy")
        
        while True:
            try:
                choice = int(input(f"Enter your choice (1-{len(strategy_list)}): "))
                if 1 <= choice <= len(strategy_list):
                    strategy_class = strategy_list[choice-1][1]
                    return strategy_class()
                print(f"Invalid choice. Please enter 1-{len(strategy_list)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    # Get strategy choices based on game mode
    if mode == GameMode.PLAYER_VS_AI:
        ai1_strategy = None
        ai2_strategy = get_strategy_choice(2)
    else:
        ai1_strategy = get_strategy_choice(1)
        ai2_strategy = get_strategy_choice(2)
    
    return mode, ai1_strategy, ai2_strategy, enable_debug

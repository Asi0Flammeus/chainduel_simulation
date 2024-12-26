from typing import Tuple, Optional, Dict, Type
import inspect
from ..common.enums import GameMode
from ..strategies.base import SnakeStrategy
from ..strategies import ai as ai_module

def get_available_strategies() -> Dict[str, Type[SnakeStrategy]]:
    strategies = {}
    for name, obj in inspect.getmembers(ai_module):
        if (inspect.isclass(obj) 
            and issubclass(obj, SnakeStrategy) 
            and obj != SnakeStrategy
            and obj.__module__ == ai_module.__name__):
            display_name = name.replace('Strategy', '')
            strategies[display_name] = obj
    return strategies

def get_strategy_choice(player_num: int) -> SnakeStrategy:
    strategies = get_available_strategies()
    strategy_list = list(strategies.items())
    
    print(f"\nAvailable strategies for AI {player_num}:")
    for i, (name, _) in enumerate(strategy_list, 1):
        print(f"{i}. {name}")
    
    while True:
        try:
            choice = int(input(f"Enter your choice (1-{len(strategy_list)}): "))
            if 1 <= choice <= len(strategy_list):
                strategy_class = strategy_list[choice-1][1]
                return strategy_class()
            print(f"Invalid choice. Please enter 1-{len(strategy_list)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_game_settings() -> Tuple[GameMode, Optional[SnakeStrategy], Optional[SnakeStrategy], bool, Optional[int]]:
    print("\nWelcome to Snake Game!")
    
    print("\nSelect Game Mode:")
    print("1. Player vs AI")
    print("2. AI vs AI")
    print("3. Simulation")
    
    while True:
        try:
            mode_choice = int(input("Enter your choice (1-3): "))
            if 1 <= mode_choice <= len(GameMode):
                mode = list(GameMode)[mode_choice-1]
                break
            print("Invalid choice. Please enter 1-3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    if mode == GameMode.SIMULATION:
        num_runs = int(input("Enter number of simulation runs: "))
        strategy1 = get_strategy_choice(1)
        strategy2 = get_strategy_choice(2)
        return mode, strategy1, strategy2, False, num_runs
    
    enable_debug = input("\nEnable debug mode? (y/n): ").lower() == 'y'
    
    if mode == GameMode.PLAYER_VS_AI:
        return mode, None, get_strategy_choice(2), enable_debug, None
    else:
        return mode, get_strategy_choice(1), get_strategy_choice(2), enable_debug, None

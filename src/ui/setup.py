# src/ui/setup.py
from typing import Tuple, Optional
from ..common.enums import GameMode, Strategy
from ..strategies.ai import RandomStrategy, FoodSeekingStrategy, AnticipationStrategy

def get_game_settings() -> Tuple[GameMode, Optional[Strategy], Optional[Strategy], bool]:
    print("\nWelcome to Snake Game!")
    
    # Ask for debug mode
    while True:
        debug_choice = input("\nEnable debug mode? (y/n): ").lower()
        if debug_choice in ['y', 'n']:
            enable_debug = debug_choice == 'y'
            break
        print("Invalid choice. Please enter 'y' or 'n'.")
    
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
    
    def get_strategy_choice(player_num: int) -> Strategy:
        print(f"\nSelect strategy for AI {player_num}:")
        for i, strategy in enumerate(Strategy, 1):
            print(f"{i}. {strategy.value}")
        while True:
            try:
                choice = int(input(f"Enter your choice (1-{len(Strategy)}): "))
                if 1 <= choice <= len(Strategy):
                    return list(Strategy)[choice-1]
                print(f"Invalid choice. Please enter 1-{len(Strategy)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    # Map strategies to their implementations
    strategy_map = {
        Strategy.RANDOM: RandomStrategy(),
        Strategy.FOOD_SEEKING: FoodSeekingStrategy(),
        Strategy.ANTICIPATION: AnticipationStrategy()
    }
    
    if mode == GameMode.PLAYER_VS_AI:
        ai1_strategy = None
        ai2_strategy = strategy_map[get_strategy_choice(2)]
    else:
        ai1_strategy = strategy_map[get_strategy_choice(1)]
        ai2_strategy = strategy_map[get_strategy_choice(2)]
    
    return mode, ai1_strategy, ai2_strategy, enable_debug

# src/ui/setup.py
from src.common.enums import GameMode  # Assuming GameMode enum is in this file
from src.strategies.ai import (SimpleFoodSeekingStrategy, AdaptiveSeekingStrategy,
                          AggressiveStrategy, NoisyAdaptiveStrategy) # Import strategies

def get_game_settings():
    """Gets game settings from the user via numbered list selection."""

    print("\nSelect Game Mode:")
    print("1. Interactive")
    print("2. Simulation")
    print("3. Full Simulation")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= 3:
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    if choice == 3:  # Full Simulation
        num_runs = input("Enter the number of simulation runs per strategy pair: ")
        output_dir = input("Enter the output directory for the CSV file: ")
        return ["full_simulation", num_runs, output_dir]

    if choice == 1:
        mode = GameMode.PLAYER_VS_AI # Or GameMode.AI_VS_AI if you want that as default
    elif choice == 2:
        mode = GameMode.SIMULATION

    strategy_choices = {
        "1": SimpleFoodSeekingStrategy,
        "2": AdaptiveSeekingStrategy,
        "3": AggressiveStrategy,
        "4": NoisyAdaptiveStrategy
    }

    print("\nSelect Strategies:")
    print("1. Simple Food Seeking")
    print("2. Adaptive Seeking")
    print("3. Aggressive")
    print("4. Noisy Adaptive")

    while True:
        try:
            strategy1_choice = input("Enter the number for Player 1's strategy: ")
            strategy2_choice = input("Enter the number for Player 2's strategy: ")

            strategy1 = strategy_choices[strategy1_choice]()
            strategy2 = strategy_choices[strategy2_choice]()
            break  # Exit the loop if strategy selection is successful
        except KeyError:
            print("Invalid strategy choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    if mode == GameMode.SIMULATION:
        num_runs = input("Enter the number of simulation runs: ")
        return [mode, strategy1, strategy2, None, num_runs]  # 'None' for enable_debug
    else:  # Interactive mode
        enable_debug_str = input("Enable debug mode? (yes/no): ").lower()
        enable_debug = enable_debug_str == "yes"
        return [mode, strategy1, strategy2, enable_debug]


import time
import statistics
import random
import os
from tqdm import tqdm
from typing import List, Tuple, Dict, Optional
from datetime import datetime

from enums import GameMode, Direction
from snake import Snake
from game_state import GameState
from constants import GameConfig

class SimulationRunner:
    def __init__(self, strategy1, strategy2, num_runs: int):
        self.strategy1 = strategy1
        self.strategy2 = strategy2
        self.num_runs = num_runs
        self.config = GameConfig()
        
        # Create simulations directory
        self.sim_dir = 'simulations'
        os.makedirs(self.sim_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run_dir = os.path.join(self.sim_dir, f'sim_{timestamp}')
        os.makedirs(self.run_dir, exist_ok=True)
        
        self.results_file = os.path.join(self.run_dir, 'results.txt')
        self.stats_file = os.path.join(self.run_dir, 'stats.txt')
        
        # Initialize statistics
        self.stats = {
            'wins1': 0,
            'wins2': 0,
            'avg_score1': [],
            'avg_score2': [],
            'max_length1': [],
            'max_length2': [],
            'game_lengths': [],
            'points_gained1': [],
            'points_gained2': [],
            'strategy1_name': strategy1.__class__.__name__,
            'strategy2_name': strategy2.__class__.__name__
        }

    def save_and_print_report(self):
        def write_report(f):
            f.write(f"=== Simulation Report ===\n")
            f.write(f"Strategies: {self.stats['strategy1_name']} vs {self.stats['strategy2_name']}\n")
            f.write(f"Total Games: {self.num_runs}\n\n")
            
            f.write("Wins:\n")
            f.write(f"Player 1: {self.stats['wins1']} ({self.stats['wins1']/self.num_runs*100:.1f}%)\n")
            f.write(f"Player 2: {self.stats['wins2']} ({self.stats['wins2']/self.num_runs*100:.1f}%)\n\n")
            
            f.write("Final Scores:\n")
            avg_score1 = statistics.mean(self.stats['avg_score1'])
            avg_score2 = statistics.mean(self.stats['avg_score2'])
            f.write(f"Player 1 - Avg: {avg_score1:,.0f}, Max: {max(self.stats['avg_score1']):,}\n")
            f.write(f"Player 2 - Avg: {avg_score2:,.0f}, Max: {max(self.stats['avg_score2']):,}\n\n")
            
            if self.stats['points_gained1']:  # Check if points were recorded
                f.write("Points per Food:\n")
                avg_points1 = statistics.mean(self.stats['points_gained1'])
                avg_points2 = statistics.mean(self.stats['points_gained2'])
                f.write(f"Player 1 - Avg: {avg_points1:,.0f}\n")
                f.write(f"Player 2 - Avg: {avg_points2:,.0f}\n\n")
            
            f.write("Snake Lengths:\n")
            avg_len1 = statistics.mean(self.stats['max_length1'])
            avg_len2 = statistics.mean(self.stats['max_length2'])
            f.write(f"Player 1 - Avg Max: {avg_len1:.1f}\n")
            f.write(f"Player 2 - Avg Max: {avg_len2:.1f}\n\n")
            
            f.write("Game Length:\n")
            avg_steps = statistics.mean(self.stats['game_lengths'])
            min_steps = min(self.stats['game_lengths'])
            max_steps = max(self.stats['game_lengths'])
            f.write(f"Average Steps: {avg_steps:.1f}\n")
            f.write(f"Min/Max Steps: {min_steps}/{max_steps}")

        with open(self.stats_file, 'w') as f:
            write_report(f)
        
        print(f"\nResults saved to: {self.run_dir}")
        with open(self.stats_file, 'r') as f:
            print(f.read())

    def run(self):  # Changed from run_simulation to run
        """Main simulation loop with progress bar."""
        with open(self.results_file, 'w') as f:
            for _ in tqdm(range(self.num_runs), desc="Running simulations"):
                result = self.run_single_game()
                f.write(f"{result}\n")
                f.flush()
                
                states = [eval(state) for state in result.split(';')]
                self.stats['game_lengths'].append(len(states))
                
                final_state = states[-1]
                score1, length1 = final_state[0]
                score2, length2 = final_state[1]
                
                self.stats['avg_score1'].append(score1)
                self.stats['avg_score2'].append(score2)
                self.stats['max_length1'].append(max(state[0][1] for state in states))
                self.stats['max_length2'].append(max(state[1][1] for state in states))
                
                if score1 > score2:
                    self.stats['wins1'] += 1
                elif score2 > score1:
                    self.stats['wins2'] += 1
        
        self.save_and_print_report()

    def _place_food(self, snake1_body: List[Tuple[int, int]], snake2_body: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Place food in a random empty cell."""
        while True:
            x = random.randint(0, self.config.GRID_WIDTH - 1)
            y = random.randint(0, self.config.GRID_HEIGHT - 1)
            if (x, y) not in snake1_body and (x, y) not in snake2_body:
                return (x, y)

    def _reset_snake(self, snake_id: int) -> List[Tuple[int, int]]:
        """Reset snake to starting position."""
        if snake_id == 1:
            return [(2 - i, self.config.GRID_HEIGHT//2) for i in range(2)]
        return [(self.config.GRID_WIDTH-3 + i, self.config.GRID_HEIGHT//2) for i in range(2)]

    def run_single_game(self) -> str:
        """Run a single simulation game and return the history."""
        game_state = GameState(
            snake1=self._reset_snake(1),
            snake2=self._reset_snake(2),
            food_position=(self.config.GRID_WIDTH // 2, self.config.GRID_HEIGHT // 2),
            grid_width=self.config.GRID_WIDTH,
            grid_height=self.config.GRID_HEIGHT,
            score1=self.config.STARTING_SCORE,
            score2=self.config.STARTING_SCORE
        )
        
        snake1 = Snake(game_state.snake1)
        snake2 = Snake(game_state.snake2)
        history = []
        max_steps = 1000
        
        while len(history) < max_steps:
            direction1 = self.strategy1.get_next_move(game_state, 1)
            direction2 = self.strategy2.get_next_move(game_state, 2)
            
            snake1.set_direction(direction1)
            snake2.set_direction(direction2)
            
            if not snake1.move(game_state.grid_width, game_state.grid_height):
                game_state.snake1 = self._reset_snake(1)
                snake1 = Snake(game_state.snake1)
            
            if not snake2.move(game_state.grid_width, game_state.grid_height):
                game_state.snake2 = self._reset_snake(2)
                snake2 = Snake(game_state.snake2)
            
            game_state.snake1 = snake1.body
            game_state.snake2 = snake2.body
            
            if snake1.check_collision(snake2):
                game_state.snake1 = self._reset_snake(1)
                snake1 = Snake(game_state.snake1)
            
            if snake2.check_collision(snake1):
                game_state.snake2 = self._reset_snake(2)
                snake2 = Snake(game_state.snake2)
            
            # Handle food collection with new scoring system
            if snake1.head == game_state.food_position:
                snake1.grow()
                points = self.config.calculate_points(len(snake1.body))
                game_state.score1 += points
                game_state.score2 -= points
                self.stats['points_gained1'].append(points)
                if game_state.score1 >= self.config.WINNING_SCORE:
                    break
                game_state.food_position = self._place_food(game_state.snake1, game_state.snake2)
            
            if snake2.head == game_state.food_position:
                snake2.grow()
                points = self.config.calculate_points(len(snake2.body))
                game_state.score2 += points
                game_state.score1 -= points
                self.stats['points_gained2'].append(points)
                if game_state.score2 >= self.config.WINNING_SCORE:
                    break
                game_state.food_position = self._place_food(game_state.snake1, game_state.snake2)
            
            history.append(([game_state.score1, len(snake1.body)], 
                          [game_state.score2, len(snake2.body)]))
        
        return ';'.join(str(state) for state in history)

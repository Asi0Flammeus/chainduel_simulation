import time
import statistics
import random
import os
from typing import Tuple, List, Dict, Optional, Any
from tqdm import tqdm
from datetime import datetime
from ..common.enums import GameMode, Direction
from ..core.snake import Snake
from ..core.game_state import GameState
from ..common.constants import GameConfig

class GameResult:
    def __init__(self):
        self.history: List[Tuple[List[int], List[int]]] = []
        self.winner: Optional[int] = None  # 1, 2, or None for draw
        self.end_type: str = "unknown"  # "win", "timeout", "draw"
        self.max_length1: int = 2
        self.max_length2: int = 2
        self.final_score1: int = 50000
        self.final_score2: int = 50000
        self.steps: int = 0
        self.points_gained1: List[int] = []
        self.points_gained2: List[int] = []

class SimulationRunner:
    def __init__(self, strategy1: Any, strategy2: Any, num_runs: int):
        self.strategy1 = strategy1
        self.strategy2 = strategy2
        self.num_runs = num_runs
        self.config = GameConfig()
        
        # Setup directories
        self.sim_dir = self._setup_directories()
        
        # Initialize statistics
        self.stats = {
            'total_games': num_runs,
            'wins': {1: 0, 2: 0, 'draw': 0},
            'timeouts': 0,
            'scores': {
                1: {'total': [], 'avg': 0, 'max': 0, 'min': float('inf')},
                2: {'total': [], 'avg': 0, 'max': 0, 'min': float('inf')}
            },
            'lengths': {
                1: {'max': [], 'avg': 0},
                2: {'max': [], 'avg': 0}
            },
            'points_per_food': {
                1: {'total': [], 'avg': 0},
                2: {'total': [], 'avg': 0}
            },
            'game_lengths': {'total': [], 'avg': 0, 'min': float('inf'), 'max': 0},
            'strategy_names': {
                1: strategy1.__class__.__name__,
                2: strategy2.__class__.__name__
            }
        }

    def _setup_directories(self) -> str:
        """Create and setup simulation directories."""
        sim_dir = 'simulations'
        os.makedirs(sim_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run_dir = os.path.join(sim_dir, f'sim_{timestamp}')
        os.makedirs(self.run_dir, exist_ok=True)
        
        self.results_file = os.path.join(self.run_dir, 'results.txt')
        self.stats_file = os.path.join(self.run_dir, 'stats.txt')
        self.detailed_file = os.path.join(self.run_dir, 'detailed.txt')
        
        return sim_dir

    def _update_stats(self, result: GameResult) -> None:
        """Update statistics based on game result."""
        # Update wins
        if result.winner:
            self.stats['wins'][result.winner] += 1
        else:
            self.stats['wins']['draw'] += 1
        
        # Update timeouts
        if result.end_type == "timeout":
            self.stats['timeouts'] += 1
        
        # Update scores
        self.stats['scores'][1]['total'].append(result.final_score1)
        self.stats['scores'][2]['total'].append(result.final_score2)
        
        # Update lengths
        self.stats['lengths'][1]['max'].append(result.max_length1)
        self.stats['lengths'][2]['max'].append(result.max_length2)
        
        # Update points per food
        if result.points_gained1:
            self.stats['points_per_food'][1]['total'].extend(result.points_gained1)
        if result.points_gained2:
            self.stats['points_per_food'][2]['total'].extend(result.points_gained2)
        
        # Update game length
        self.stats['game_lengths']['total'].append(result.steps)
        self.stats['game_lengths']['min'] = min(self.stats['game_lengths']['min'], result.steps)
        self.stats['game_lengths']['max'] = max(self.stats['game_lengths']['max'], result.steps)

    def _calculate_final_stats(self) -> None:
        """Calculate final statistics after all games."""
        for player in [1, 2]:
            scores = self.stats['scores'][player]['total']
            self.stats['scores'][player]['avg'] = statistics.mean(scores)
            self.stats['scores'][player]['max'] = max(scores)
            self.stats['scores'][player]['min'] = min(scores)
            
            self.stats['lengths'][player]['avg'] = statistics.mean(self.stats['lengths'][player]['max'])
            
            if self.stats['points_per_food'][player]['total']:
                self.stats['points_per_food'][player]['avg'] = statistics.mean(
                    self.stats['points_per_food'][player]['total']
                )
        
        self.stats['game_lengths']['avg'] = statistics.mean(self.stats['game_lengths']['total'])

    def run_single_game(self) -> GameResult:
        """Run a single simulation game and return the result."""
        result = GameResult()
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
        max_steps = 1000
        
        while len(result.history) < max_steps:
            direction1 = self.strategy1.get_next_move(game_state, 1)
            direction2 = self.strategy2.get_next_move(game_state, 2)
            
            # Move snakes
            snake1.set_direction(direction1)
            snake2.set_direction(direction2)
            
            # Handle wall collisions
            if not snake1.move(game_state.grid_width, game_state.grid_height):
                game_state.snake1 = self._reset_snake(1)
                snake1 = Snake(game_state.snake1)
            
            if not snake2.move(game_state.grid_width, game_state.grid_height):
                game_state.snake2 = self._reset_snake(2)
                snake2 = Snake(game_state.snake2)
            
            game_state.snake1 = snake1.body
            game_state.snake2 = snake2.body
            
            # Handle snake collisions
            if snake1.check_collision(snake2):
                game_state.snake1 = self._reset_snake(1)
                snake1 = Snake(game_state.snake1)
            
            if snake2.check_collision(snake1):
                game_state.snake2 = self._reset_snake(2)
                snake2 = Snake(game_state.snake2)
            
            # Handle food collection
            if snake1.head == game_state.food_position:
                snake1.grow()
                points = self.config.calculate_points(len(snake1.body))
                game_state.score1 += points
                game_state.score2 -= points
                result.points_gained1.append(points)
                if game_state.score1 >= self.config.WINNING_SCORE:
                    result.winner = 1
                    result.end_type = "win"
                    break
                game_state.food_position = self._place_food(game_state.snake1, game_state.snake2)
            
            if snake2.head == game_state.food_position:
                snake2.grow()
                points = self.config.calculate_points(len(snake2.body))
                game_state.score2 += points
                game_state.score1 -= points
                result.points_gained2.append(points)
                if game_state.score2 >= self.config.WINNING_SCORE:
                    result.winner = 2
                    result.end_type = "win"
                    break
                game_state.food_position = self._place_food(game_state.snake1, game_state.snake2)
            
            # Update history
            result.history.append(([game_state.score1, len(snake1.body)], 
                                 [game_state.score2, len(snake2.body)]))
        
        # Set final game result data
        result.steps = len(result.history)
        result.max_length1 = max(state[0][1] for state in result.history)
        result.max_length2 = max(state[1][1] for state in result.history)
        result.final_score1 = game_state.score1
        result.final_score2 = game_state.score2
        
        # Set end type if not already set
        if not result.winner:
            if len(result.history) >= max_steps:
                result.end_type = "timeout"
            else:
                result.end_type = "draw"
            
            # Determine winner based on final score if not a win condition
            if game_state.score1 > game_state.score2:
                result.winner = 1
            elif game_state.score2 > game_state.score1:
                result.winner = 2
        
        return result

    def _reset_snake(self, snake_id: int) -> List[Tuple[int, int]]:
        """Reset snake to starting position."""
        if snake_id == 1:
            return [(2 - i, self.config.GRID_HEIGHT//2) for i in range(2)]
        return [(self.config.GRID_WIDTH-3 + i, self.config.GRID_HEIGHT//2) for i in range(2)]

    def _place_food(self, snake1_body: List[Tuple[int, int]], snake2_body: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Place food in a random empty cell."""
        while True:
            x = random.randint(0, self.config.GRID_WIDTH - 1)
            y = random.randint(0, self.config.GRID_HEIGHT - 1)
            if (x, y) not in snake1_body and (x, y) not in snake2_body:
                return (x, y)

    def save_report(self) -> None:
        """Generate and save simulation report."""
        with open(self.stats_file, 'w') as f:
            f.write(f"=== Simulation Report ===\n")
            f.write(f"Strategies: {self.stats['strategy_names'][1]} vs {self.stats['strategy_names'][2]}\n")
            f.write(f"Total Games: {self.stats['total_games']}\n\n")
            
            f.write("Wins:\n")
            f.write(f"Player 1: {self.stats['wins'][1]} ({self.stats['wins'][1]/self.num_runs*100:.1f}%)\n")
            f.write(f"Player 2: {self.stats['wins'][2]} ({self.stats['wins'][2]/self.num_runs*100:.1f}%)\n")
            f.write(f"Draws: {self.stats['wins']['draw']} ({self.stats['wins']['draw']/self.num_runs*100:.1f}%)\n")
            f.write(f"Timeouts: {self.stats['timeouts']} ({self.stats['timeouts']/self.num_runs*100:.1f}%)\n\n")
            
            f.write("Final Scores:\n")
            for player in [1, 2]:
                f.write(f"Player {player}:\n")
                f.write(f"  Avg: {self.stats['scores'][player]['avg']:,.0f}\n")
                f.write(f"  Max: {self.stats['scores'][player]['max']:,}\n")
                f.write(f"  Min: {self.stats['scores'][player]['min']:,}\n")
            f.write("\n")
            
            f.write("Points per Food:\n")
            for player in [1, 2]:
                if self.stats['points_per_food'][player]['total']:
                    f.write(f"Player {player} - Avg: {self.stats['points_per_food'][player]['avg']:,.0f}\n")
            f.write("\n")
            
            f.write("Snake Lengths:\n")
            for player in [1, 2]:
                f.write(f"Player {player} - Avg Max: {self.stats['lengths'][player]['avg']:.1f}\n")
            f.write("\n")
            
            f.write("Game Length:\n")
            f.write(f"Average Steps: {self.stats['game_lengths']['avg']:.1f}\n")
            f.write(f"Min/Max Steps: {self.stats['game_lengths']['min']}/{self.stats['game_lengths']['max']}")

    def run(self) -> None:
        """Run all simulations and generate report."""
        with open(self.detailed_file, 'w') as detailed_f:
            detailed_f.write("Game,Winner,EndType,Steps,Score1,Score2,MaxLength1,MaxLength2\n")
            
            for game_num in tqdm(range(self.num_runs), desc="Running simulations"):
                # Run game and get result
                result = self.run_single_game()
                
                # Update statistics
                self._update_stats(result)
                
                # Write detailed game data
                detailed_f.write(
                    f"{game_num},{result.winner},{result.end_type},{result.steps},"
                    f"{result.final_score1},{result.final_score2},"
                    f"{result.max_length1},{result.max_length2}\n"
                )
                detailed_f.flush()
        
        # Calculate final statistics
        self._calculate_final_stats()
        
        # Save and display report
        self.save_report()
        print(f"\nResults saved to: {self.run_dir}")
        with open(self.stats_file, 'r') as f:
            print(f.read())

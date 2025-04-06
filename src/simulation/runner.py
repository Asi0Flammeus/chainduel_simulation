from typing import Tuple, List, Dict, Any
from tqdm import tqdm
from datetime import datetime
import os
import random
import statistics
from ..common.enums import Direction
from ..core.snake import Snake
from ..core.game_state import GameState
from ..common.constants import GameConfig

class InitialPosition:
    def __init__(self, x: int, y: int, direction: Direction, description: str):
        self.x = x
        self.y = y
        self.direction = direction
        self.description = description

class ScenarioSimulationRunner:
    def __init__(self, strategy1, strategy2, num_runs: int):
        self.strategy1 = strategy1
        self.strategy2 = strategy2
        self.num_runs = num_runs
        self.config = GameConfig()
        
        # Create output directory
        self.sim_dir = 'scenario_simulations'
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
            'strategy1_name': strategy1.__class__.__name__,
            'strategy2_name': strategy2.__class__.__name__,
            'position_stats': {}  # Stats per starting position
        }

    def generate_snake2_positions(self) -> List[InitialPosition]:
        """Generate the three specific starting positions for snake 2."""
        center_y = self.config.GRID_HEIGHT // 2
        center_x = self.config.GRID_WIDTH // 2
        
        # These positions match the screenshots exactly
        positions = [
            InitialPosition(
                x=center_x + 2,
                y=center_y,
                direction=Direction.LEFT,
                description="Right of center"
            ),
            InitialPosition(
                x=center_x +1, 
                y=center_y +1,
                direction=Direction.LEFT,
                description="Further right"
            ),
            InitialPosition(
                x=center_x + 2,
                y=center_y + 2,
                direction=Direction.LEFT,
                description="Furthest right"
            )
        ]
        
        return positions

    def init_specific_scenario(self, snake2_pos: InitialPosition) -> GameState:
        """Initialize game state with specific scenario conditions."""
        center_x = self.config.GRID_WIDTH // 2
        center_y = self.config.GRID_HEIGHT // 2
        
        # Snake 1 has just eaten first food at center
        # Length 3, starting from center moving left
        snake1 = [
            (center_x, center_y),      # Head at center (just ate food)
            (center_x-1, center_y),    # Body
            (center_x-2, center_y)     # Tail
        ]
        
        # Snake 2 at specified position
        x2, y2 = snake2_pos.x, snake2_pos.y
        snake2 = [
            (x2, y2),                  # Head
            (x2 + 1, y2)              # Tail (one segment to right since moving left)
        ]
        
        # Create new game state
        state = GameState(
            snake1=snake1,
            snake2=snake2,
            food_position=self._place_food(snake1, snake2),  # New random food
            grid_width=self.config.GRID_WIDTH,
            grid_height=self.config.GRID_HEIGHT,
            score1=self.config.STARTING_SCORE + 2000,  # Adjusted for first food
            score2=self.config.STARTING_SCORE - 2000
        )
        
        return state

    def _place_food(self, snake1_body: List[Tuple[int, int]], snake2_body: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Place food in a random empty cell."""
        while True:
            x = random.randint(0, self.config.GRID_WIDTH - 1)
            y = random.randint(0, self.config.GRID_HEIGHT - 1)
            if (x, y) not in snake1_body and (x, y) not in snake2_body:
                return (x, y)

    def run_single_game(self, snake2_pos: InitialPosition) -> str:
        """Run a single game with specific starting conditions."""
        game_state = self.init_specific_scenario(snake2_pos)
        
        snake1 = Snake(game_state.snake1, Direction.LEFT)  # Set initial direction
        snake2 = Snake(game_state.snake2, snake2_pos.direction)
        history = []
        max_steps = 1000
        
        while len(history) < max_steps:
            direction1 = self.strategy1.get_next_move(game_state, 1)
            direction2 = self.strategy2.get_next_move(game_state, 2)
            
            snake1.set_direction(direction1)
            snake2.set_direction(direction2)
            
            if not snake1.move(game_state.grid_width, game_state.grid_height):
                game_state.snake1 = [(2 - i, self.config.GRID_HEIGHT//2) for i in range(3)]
                snake1 = Snake(game_state.snake1, Direction.RIGHT)
            
            if not snake2.move(game_state.grid_width, game_state.grid_height):
                game_state.snake2 = [(self.config.GRID_WIDTH-3 + i, self.config.GRID_HEIGHT//2) for i in range(2)]
                snake2 = Snake(game_state.snake2, Direction.LEFT)
            
            game_state.snake1 = snake1.body
            game_state.snake2 = snake2.body
            
            if snake1.check_collision(snake2):
                game_state.snake1 = [(2 - i, self.config.GRID_HEIGHT//2) for i in range(3)]
                snake1 = Snake(game_state.snake1, Direction.RIGHT)
            
            if snake2.check_collision(snake1):
                game_state.snake2 = [(self.config.GRID_WIDTH-3 + i, self.config.GRID_HEIGHT//2) for i in range(2)]
                snake2 = Snake(game_state.snake2, Direction.LEFT)
            
            # Handle food collection
            if snake1.head == game_state.food_position:
                snake1.grow()
                points = self.config.calculate_points(len(snake1.body))
                game_state.score1 += points
                game_state.score2 -= points
                if game_state.score1 >= self.config.WINNING_SCORE:
                    break
                game_state.food_position = self._place_food(game_state.snake1, game_state.snake2)
            
            if snake2.head == game_state.food_position:
                snake2.grow()
                points = self.config.calculate_points(len(snake2.body))
                game_state.score2 += points
                game_state.score1 -= points
                if game_state.score2 >= self.config.WINNING_SCORE:
                    break
                game_state.food_position = self._place_food(game_state.snake1, game_state.snake2)
            
            history.append(([game_state.score1, len(snake1.body)], 
                          [game_state.score2, len(snake2.body)]))
        
        return ';'.join(str(state) for state in history)

    def run(self):
        """Run simulations for each starting position."""
        positions = self.generate_snake2_positions()
        
        for pos in positions:
            pos_key = f"Position {pos.description}"
            self.stats['position_stats'][pos_key] = {
                'wins1': 0,
                'wins2': 0,
                'avg_score1': [],
                'avg_score2': [],
            }
            
            print(f"\nRunning simulations for Snake 2 {pos.description}")
            for _ in tqdm(range(self.num_runs), desc="Progress"):
                result = self.run_single_game(pos)
                
                states = [eval(state) for state in result.split(';')]
                final_state = states[-1]
                score1, length1 = final_state[0]
                score2, length2 = final_state[1]
                
                # Update global stats
                self.stats['avg_score1'].append(score1)
                self.stats['avg_score2'].append(score2)
                self.stats['max_length1'].append(max(state[0][1] for state in states))
                self.stats['max_length2'].append(max(state[1][1] for state in states))
                self.stats['game_lengths'].append(len(states))
                
                # Update position-specific stats
                self.stats['position_stats'][pos_key]['avg_score1'].append(score1)
                self.stats['position_stats'][pos_key]['avg_score2'].append(score2)
                
                if score1 > score2:
                    self.stats['wins1'] += 1
                    self.stats['position_stats'][pos_key]['wins1'] += 1
                else:
                    self.stats['wins2'] += 1
                    self.stats['position_stats'][pos_key]['wins2'] += 1
        
        self.save_and_print_report()

    def save_and_print_report(self):
        """Generate and save detailed simulation report."""
        with open(self.stats_file, 'w') as f:
            f.write(f"=== Specific Scenario Simulation Report ===\n")
            f.write(f"Strategies: {self.stats['strategy1_name']} vs {self.stats['strategy2_name']}\n")
            f.write(f"Total Games: {self.num_runs * len(self.stats['position_stats'])}\n\n")
            
            f.write("Overall Results:\n")
            total_games = self.num_runs * len(self.stats['position_stats'])
            f.write(f"Player 1: {self.stats['wins1']} ({self.stats['wins1']/total_games*100:.1f}%)\n")
            f.write(f"Player 2: {self.stats['wins2']} ({self.stats['wins2']/total_games*100:.1f}%)\n\n")
            
            f.write("Results by Starting Position:\n")
            for pos_key, pos_stats in self.stats['position_stats'].items():
                f.write(f"\n{pos_key}:\n")
                f.write(f"  Wins P1: {pos_stats['wins1']} ({pos_stats['wins1']/self.num_runs*100:.1f}%)\n")
                f.write(f"  Wins P2: {pos_stats['wins2']} ({pos_stats['wins2']/self.num_runs*100:.1f}%)\n")
                f.write(f"  Avg Score P1: {statistics.mean(pos_stats['avg_score1']):,.0f}\n")
                f.write(f"  Avg Score P2: {statistics.mean(pos_stats['avg_score2']):,.0f}\n")
            
            f.write("\nOverall Statistics:\n")
            f.write(f"Average Game Length: {statistics.mean(self.stats['game_lengths']):.1f} steps\n")
            f.write(f"Max Snake Lengths - P1: {max(self.stats['max_length1'])}, P2: {max(self.stats['max_length2'])}\n")
        
        print(f"\nResults saved to: {self.run_dir}")
        with open(self.stats_file, 'r') as f:
            print(f.read())

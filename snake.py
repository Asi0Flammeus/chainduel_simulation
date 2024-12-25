import tkinter as tk
from dataclasses import dataclass
from typing import List, Tuple, Callable, Optional
from enum import Enum, auto
import random
import time
import math


# ====== Enums and Data Classes ======
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @classmethod
    def opposite(cls, direction: 'Direction') -> 'Direction':
        if direction == cls.UP: return cls.DOWN
        if direction == cls.DOWN: return cls.UP
        if direction == cls.LEFT: return cls.RIGHT
        if direction == cls.RIGHT: return cls.LEFT


class GameMode(Enum):
    PLAYER_VS_AI = "Player vs AI"
    AI_VS_AI = "AI vs AI"


class Strategy(Enum):
    RANDOM = "Random Movement"
    FOOD_SEEKING = "Food Seeking"
    ANTICIPATION = "Anticipation"


@dataclass
class GameConfig:
    width: int = 800
    height: int = 600
    grid_size: int = 20
    fps: int = 15
    initial_length: int = 3


@dataclass
class GameState:
    snake1: List[Tuple[int, int]]
    snake2: List[Tuple[int, int]]
    food_position: Tuple[int, int]
    grid_width: int
    grid_height: int
    score1: int = 0
    score2: int = 0


# ====== AI Strategies ======
class AIStrategies:
    @staticmethod
    def random_strategy(state: GameState, snake_id: int) -> Direction:
        return random.choice(list(Direction))
    
    @staticmethod
    def food_seeking_strategy(state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        
        possible_moves = []
        for direction in Direction:
            new_x = head_x + direction.value[0]
            new_y = head_y + direction.value[1]
            if (0 <= new_x < state.grid_width and 
                0 <= new_y < state.grid_height and 
                (new_x, new_y) not in snake):
                dist = abs(food_x - new_x) + abs(food_y - new_y)
                possible_moves.append((dist, direction))
        
        if possible_moves:
            return min(possible_moves, key=lambda x: x[0])[1]
        return random.choice(list(Direction))
    
    @staticmethod
    def anticipation_strategy(state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        opp_x, opp_y = opponent[0]
        food_x, food_y = state.food_position
        
        # Calculate distances
        my_food_dist = math.sqrt((food_x - head_x)**2 + (food_y - head_y)**2)
        opp_food_dist = math.sqrt((food_x - opp_x)**2 + (food_y - opp_y)**2)
        
        # Choose target based on distances
        if my_food_dist > opp_food_dist:
            # Go to opposite side of food relative to opponent
            target_x = food_x + (food_x - opp_x)
            target_y = food_y + (food_y - opp_y)
            target_x = max(0, min(target_x, state.grid_width - 1))
            target_y = max(0, min(target_y, state.grid_height - 1))
        else:
            target_x, target_y = food_x, food_y
        
        # Find best move towards target
        possible_moves = []
        for direction in Direction:
            new_x = head_x + direction.value[0]
            new_y = head_y + direction.value[1]
            if (0 <= new_x < state.grid_width and 
                0 <= new_y < state.grid_height and 
                (new_x, new_y) not in snake):
                dist = abs(target_x - new_x) + abs(target_y - new_y)
                possible_moves.append((dist, direction))
        
        if possible_moves:
            return min(possible_moves, key=lambda x: x[0])[1]
        return random.choice(list(Direction))


# ====== Main Game Class ======
class SnakeGame(tk.Canvas):
    def __init__(self, master: tk.Tk, mode: GameMode, config: GameConfig, 
                 ai1_strategy: Optional[Strategy] = None, 
                 ai2_strategy: Optional[Strategy] = None):
        super().__init__(
            master, 
            width=config.width,
            height=config.height,
            bg='black',
            highlightthickness=0
        )
        
        self.config = config
        self.cells_width = config.width // config.grid_size
        self.cells_height = config.height // config.grid_size
        
        # Game settings
        self.mode = mode
        self.strategy_map = {
            Strategy.RANDOM: AIStrategies.random_strategy,
            Strategy.FOOD_SEEKING: AIStrategies.food_seeking_strategy,
            Strategy.ANTICIPATION: AIStrategies.anticipation_strategy
        }
        self.ai1_strategy = self.strategy_map[ai1_strategy] if ai1_strategy else None
        self.ai2_strategy = self.strategy_map[ai2_strategy] if ai2_strategy else None
        
        self.reset_game()
        self.bind_keys()
        self.start_game_loop()
    
    def reset_game(self):
        # Initialize snakes with more space between them
        center_y = self.cells_height // 2
        self.snake1 = [(x, center_y) for x in range(2, 2 + self.config.initial_length)]
        self.snake2 = [(self.cells_width - 3 - x, center_y) 
                      for x in range(self.config.initial_length)]
        
        # Initialize other game state
        self.food_position = self._place_food()
        self.score1 = self.score2 = 0
        
        # Reset directions
        if self.mode == GameMode.PLAYER_VS_AI:
            self.direction1 = None  # Wait for player input
            self.next_direction1 = None
        else:
            self.direction1 = Direction.RIGHT
            self.next_direction1 = Direction.RIGHT
            
        self.direction2 = Direction.LEFT
        self.next_direction2 = Direction.LEFT
        
        self.game_active = True
        self.last_update = time.time()
        
        # Initialize other game state
        self.food_position = self._place_food()
        self.score1 = self.score2 = 0
        self.direction1 = Direction.RIGHT
        self.direction2 = Direction.LEFT
        self.next_direction1 = Direction.RIGHT
        self.next_direction2 = Direction.LEFT
        self.game_active = True
        self.last_update = time.time()
    
    def bind_keys(self):
        if self.mode == GameMode.PLAYER_VS_AI:
            self.master.bind('<Key>', self.handle_keypress)
        self.master.bind('r', lambda _: self.reset_game())
        self.master.bind('<Escape>', lambda _: self.master.destroy())
    
    def handle_keypress(self, event):
        key = event.keysym.lower()
        
        # Player 1 controls (WASD)
        if self.mode == GameMode.PLAYER_VS_AI:
            if key == 'w' and (self.direction1 is None or self.direction1 != Direction.DOWN):
                self.next_direction1 = Direction.UP
                self.direction1 = Direction.UP if self.direction1 is None else self.direction1
            elif key == 's' and (self.direction1 is None or self.direction1 != Direction.UP):
                self.next_direction1 = Direction.DOWN
                self.direction1 = Direction.DOWN if self.direction1 is None else self.direction1
            elif key == 'a' and (self.direction1 is None or self.direction1 != Direction.RIGHT):
                self.next_direction1 = Direction.LEFT
                self.direction1 = Direction.LEFT if self.direction1 is None else self.direction1
            elif key == 'd' and (self.direction1 is None or self.direction1 != Direction.LEFT):
                self.next_direction1 = Direction.RIGHT
                self.direction1 = Direction.RIGHT if self.direction1 is None else self.direction1
    
    def _place_food(self) -> Tuple[int, int]:
        while True:
            x = random.randint(0, self.cells_width - 1)
            y = random.randint(0, self.cells_height - 1)
            if (x, y) not in self.snake1 and (x, y) not in self.snake2:
                return (x, y)
    
    def get_game_state(self) -> GameState:
        return GameState(
            snake1=self.snake1.copy(),
            snake2=self.snake2.copy(),
            food_position=self.food_position,
            grid_width=self.cells_width,
            grid_height=self.cells_height,
            score1=self.score1,
            score2=self.score2
        )
    
    def move_snake(self, snake_id: int) -> Tuple[bool, Optional[int]]:
        snake = self.snake1 if snake_id == 1 else self.snake2
        direction = self.next_direction1 if snake_id == 1 else self.next_direction2
        
        # Don't move if direction hasn't been set yet
        if direction is None:
            return True, None
        
        head_x, head_y = snake[0]
        new_head = (
            head_x + direction.value[0],
            head_y + direction.value[1]
        )
        
        # Check wall collisions
        if not (0 <= new_head[0] < self.cells_width and 
                0 <= new_head[1] < self.cells_height):
            return False, 3 - snake_id  # Other snake gets the point
            
        # Check snake collisions
        other_snake = self.snake2 if snake_id == 1 else self.snake1
        if new_head in snake[1:]:  # Self collision
            return False, 3 - snake_id  # Other snake gets the point
        if new_head in other_snake:  # Collision with other snake
            return False, 3 - snake_id  # Other snake gets the point
        
        # Move snake
        snake.insert(0, new_head)
        if new_head == self.food_position:
            if snake_id == 1:
                self.score1 += 1
            else:
                self.score2 += 1
            self.food_position = self._place_food()
        else:
            snake.pop()
        
        return True, None
        
        # Move snake
        if snake_id == 1:
            self.snake1.insert(0, new_head)
            self.direction1 = self.next_direction1
            if new_head == self.food_position:
                self.score1 += 1
                self.food_position = self._place_food()
            else:
                self.snake1.pop()
        else:
            self.snake2.insert(0, new_head)
            self.direction2 = self.next_direction2
            if new_head == self.food_position:
                self.score2 += 1
                self.food_position = self._place_food()
            else:
                self.snake2.pop()
        
        return True
    
    def update_game(self):
        if self.game_active:
            current_time = time.time()
            if current_time - self.last_update >= 1.0/self.config.fps:
                # Get AI moves
                state = self.get_game_state()
                
                if self.mode == GameMode.AI_VS_AI:
                    self.next_direction1 = self.ai1_strategy(state, 1)
                    self.next_direction2 = self.ai2_strategy(state, 2)
                elif self.mode == GameMode.PLAYER_VS_AI:
                    self.next_direction2 = self.ai2_strategy(state, 2)
                
                # Move snakes
                valid1, scorer1 = self.move_snake(1)
                valid2, scorer2 = self.move_snake(2)
                
                # Update scores based on collisions
                if scorer1 is not None:
                    if scorer1 == 1:
                        self.score1 += 1
                    else:
                        self.score2 += 1
                if scorer2 is not None:
                    if scorer2 == 1:
                        self.score1 += 1
                    else:
                        self.score2 += 1
                
                # Update game state
                if not valid1 or not valid2:
                    self.game_active = False
                
                self.last_update = current_time
        
        self.draw_game()
        self.after(16, self.update_game)  # ~60 FPS rendering
    
    def draw_game(self):
        self.delete('all')
        
        # Draw grid
        for i in range(0, self.cells_width + 1):
            x = i * self.config.grid_size
            self.create_line(x, 0, x, self.config.height, fill='#333333')
        for i in range(0, self.cells_height + 1):
            y = i * self.config.grid_size
            self.create_line(0, y, self.config.width, y, fill='#333333')
        
        # Draw snakes
        self._draw_snake(self.snake1, '#2ecc71')  # Green
        self._draw_snake(self.snake2, '#e67e22')  # Orange
        
        # Draw food
        x, y = self.food_position
        self.create_oval(
            x * self.config.grid_size + 2, y * self.config.grid_size + 2,
            (x + 1) * self.config.grid_size - 2, (y + 1) * self.config.grid_size - 2,
            fill='yellow'
        )
        
        # Draw scores
        self.create_text(
            50, 20, text=f'Green: {self.score1}',
            fill='#2ecc71', font=('Arial', 16, 'bold')
        )
        self.create_text(
            self.config.width - 50, 20, text=f'Orange: {self.score2}',
            fill='#e67e22', font=('Arial', 16, 'bold')
        )
        
        if not self.game_active:
            self.create_text(
                self.config.width/2, self.config.height/2,
                text='GAME OVER\nPress R to restart',
                fill='white', font=('Arial', 24, 'bold'),
                justify='center'
            )
    
    def _draw_snake(self, snake: List[Tuple[int, int]], color: str):
        for x, y in snake:
            self.create_rectangle(
                x * self.config.grid_size, y * self.config.grid_size,
                (x + 1) * self.config.grid_size, (y + 1) * self.config.grid_size,
                fill=color, outline=''
            )
    
    def start_game_loop(self):
        self.update_game()


# ====== Game Setup and Main ======
def get_game_settings() -> Tuple[GameMode, Optional[Strategy], Optional[Strategy]]:
    print("\nWelcome to Snake Game!")
    print("\nSelect Game Mode:")
    for i, mode in enumerate(GameMode, 1):
        print(f"{i}. {mode.value}")
    
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
    
    if mode == GameMode.PLAYER_VS_AI:
        ai1_strategy = None
        ai2_strategy = get_strategy_choice(2)
    else:
        ai1_strategy = get_strategy_choice(1)
        ai2_strategy = get_strategy_choice(2)
    
    return mode, ai1_strategy, ai2_strategy


def main():
    # Get game settings
    mode, ai1_strategy, ai2_strategy = get_game_settings()
    
    # Create window
    root = tk.Tk()
    root.title("Snake Game")
    
    # Configure game
    config = GameConfig()
    
    # Center window on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - config.width) // 2
    y = (screen_height - config.height) // 2
    root.geometry(f'{config.width}x{config.height}+{x}+{y}')
    
    # Create game instance
    game = SnakeGame(root, mode, config, ai1_strategy, ai2_strategy)
    game.pack(expand=True, fill='both')
    
    # Add control instructions
    if mode == GameMode.PLAYER_VS_AI:
        controls_text = "Controls: WASD (Blue) | R: Restart | ESC: Quit"
    else:
        controls_text = "Controls: R: Restart | ESC: Quit"
    
    controls = tk.Label(root, text=controls_text, bg='black', fg='white')
    controls.pack(side='bottom')
    
    # Start game
    root.mainloop()


if __name__ == "__main__":
    main()

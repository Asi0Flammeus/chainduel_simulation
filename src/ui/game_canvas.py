from __future__ import annotations
import tkinter as tk
from typing import Tuple, Optional, List, Dict, Any
import time
import random
from src.utils.debug import DebugLogger
from src.common.enums import GameMode, Direction
from src.common.types import GameState
from src.common.constants import GameConfig

Position = Tuple[int, int]

class GameCanvas(tk.Canvas):
    def __init__(self, 
                 master: tk.Tk,
                 mode: GameMode,
                 config: GameConfig = None,
                 strategy1: Optional[Any] = None,
                 strategy2: Optional[Any] = None,
                 debug: Optional[DebugLogger] = None,
                 max_score: int = 2000) -> None:
        self.game_over = False
        self.winner = None
        self.config = config or GameConfig()
        
        super().__init__(
            master,
            width=self.config.WINDOW_WIDTH,
            height=self.config.WINDOW_HEIGHT,
            bg=self.config.BACKGROUND_COLOR,
            highlightthickness=0
        )
        
        self.debug = debug or DebugLogger(False)
        self.mode = mode
        self.strategy1 = strategy1
        self.strategy2 = strategy2
        
        self.width = self.config.WINDOW_WIDTH
        self.height = self.config.WINDOW_HEIGHT
        self.cell_size = self.config.GRID_SIZE
        self.grid_width = self.config.GRID_WIDTH
        self.grid_height = self.config.GRID_HEIGHT
        
        self.max_score = self.config.MAX_SCORE
        self.score1 = 0
        self.score2 = 0
        
        self._first_food = True
        self.last_move_time = time.time()
        
        # Initialize game state
        self.snake1 = []
        self.snake2 = []
        self.food_pos = (0, 0)
        self.direction1 = Direction.RIGHT
        self.direction2 = Direction.LEFT
        
        self.reset_positions()
        self.bind_all('<Key>', self.handle_keypress)
        self.after(16, self.update_game)

    def handle_keypress(self, event: tk.Event) -> None:
        key = event.keysym
        
        if key == 'r':
            self.reset_game()
            return
        if key == 'Escape':
            self.master.destroy()
            return
            
        if self.mode == GameMode.PLAYER_VS_AI:
            key_to_direction = {
                'Up': Direction.UP,
                'Down': Direction.DOWN,
                'Left': Direction.LEFT,
                'Right': Direction.RIGHT
            }
            if key in key_to_direction:
                new_dir = key_to_direction[key]
                if not Direction.opposite(new_dir) == self.direction1:
                    self.direction1 = new_dir

    def reset_snake(self, snake_id: int) -> None:
        if snake_id == 1:
            self.snake1 = [(2 - i, self.grid_height//2) for i in range(2)]
            self.direction1 = Direction.RIGHT
        else:
            self.snake2 = [(self.grid_width-3 + i, self.grid_height//2) for i in range(2)]
            self.direction2 = Direction.LEFT

    def reset_positions(self) -> None:
        self.reset_snake(1)
        self.reset_snake(2)
        self._first_food = True
        self.food_pos = self._place_food()

    def reset_game(self) -> None:
        self.score1 = 0
        self.score2 = 0
        self.reset_positions()

    def _place_food(self) -> Position:
        if self._first_food:
            x = self.grid_width // 2
            y = self.grid_height // 2
            self._first_food = False
        else:
            while True:
                x = random.randint(0, self.grid_width - 1)
                y = random.randint(0, self.grid_height - 1)
                if (x, y) not in self.snake1 and (x, y) not in self.snake2:
                    break
        return (x, y)

    def move_snake(self, snake: List[Position], direction: Direction) -> List[Position]:
        head_x, head_y = snake[0]
        dx, dy = direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Keep old position if moving into wall
        if not (0 <= new_head[0] < self.grid_width and 0 <= new_head[1] < self.grid_height):
            return snake
            
        new_snake = [new_head] + snake[:-1]
        if new_head == self.food_pos:
            new_snake = [new_head] + snake  # Grow snake
            return new_snake
            
        return new_snake

    def check_collisions(self) -> None:
        head1 = self.snake1[0]
        head2 = self.snake2[0]
        
        # Check wall collisions
        if not (0 <= head1[0] < self.grid_width and 0 <= head1[1] < self.grid_height):
            self.reset_snake(1)
        if not (0 <= head2[0] < self.grid_width and 0 <= head2[1] < self.grid_height):
            self.reset_snake(2)
            
        # Check self collisions
        if head1 in self.snake1[1:]:
            self.reset_snake(1)
        if head2 in self.snake2[1:]:
            self.reset_snake(2)
            
        # Check head-to-head collision
        if head1 == head2:
            self.reset_snake(1)
            self.reset_snake(2)
            return
            
        # Check head to body collisions
        if head1 in self.snake2[1:]:
            self.reset_snake(1)
        if head2 in self.snake1[1:]:
            self.reset_snake(2)

    def update_game(self) -> None:
        if self.game_over:
            self.draw_game()
            return
        current_time = time.time()
        if current_time - self.last_move_time >= 0.1:
            # Get AI moves
            if self.mode == GameMode.AI_VS_AI:
                state = GameState(
                    snake1=self.snake1.copy(),
                    snake2=self.snake2.copy(),
                    food_position=self.food_pos,
                    grid_width=self.grid_width,
                    grid_height=self.grid_height,
                    score1=self.score1,
                    score2=self.score2
                )
                if self.strategy1:
                    self.direction1 = self.strategy1.get_next_move(state, 1)
                if self.strategy2:
                    self.direction2 = self.strategy2.get_next_move(state, 2)
            elif self.mode == GameMode.PLAYER_VS_AI and self.strategy2:
                state = GameState(
                    snake1=self.snake1.copy(),
                    snake2=self.snake2.copy(),
                    food_position=self.food_pos,
                    grid_width=self.grid_width,
                    grid_height=self.grid_height,
                    score1=self.score1,
                    score2=self.score2
                )
                self.direction2 = self.strategy2.get_next_move(state, 2)

            # Move snakes
            old_len1 = len(self.snake1)
            old_len2 = len(self.snake2)
            
            self.snake1 = self.move_snake(self.snake1, self.direction1)
            self.snake2 = self.move_snake(self.snake2, self.direction2)
            
            # Check if food was collected and update scores
            if len(self.snake1) > old_len1:
                points = old_len1  # Points = snake length
                # self.score1 += points
                self.score1 += 1
                if self.score1 >= self.max_score:
                    self.game_over = True
                    self.winner = "Green"
                self.food_pos = self._place_food()
            elif len(self.snake2) > old_len2:
                points = old_len2  # Points = snake length
                # self.score2 += points
                self.score2 += 1
                if self.score2 >= self.max_score:
                    self.game_over = True
                    self.winner = "Orange"
                self.food_pos = self._place_food()
            
            # Handle all collisions
            self.check_collisions()
            
            self.last_move_time = current_time
        
        self.draw_game()
        self.after(16, self.update_game)

    def draw_game(self) -> None:
        if self.game_over:
            self.delete('all')
            self.create_text(
                self.width // 2,
                self.height // 2,
                text=f"Game Over!\n{self.winner} Wins!\nScore: {max(self.score1, self.score2)}",
                fill='white',
                font=('Arial', 24, 'bold'),
                justify='center'
            )
            return
        self.delete('all')
        
        # Draw grid
        for i in range(0, self.width + 1, self.cell_size):
            self.create_line(i, 0, i, self.height, fill=self.config.GRID_COLOR)
        for i in range(0, self.height + 1, self.cell_size):
            self.create_line(0, i, self.width, i, fill=self.config.GRID_COLOR)
        
        # Draw snakes
        for snake_positions, head_color, base_color in [
            (self.snake1, self.config.SNAKE1_COLOR, '#164a29'),
            (self.snake2, self.config.SNAKE2_COLOR, '#a65602')
        ]:
            # Draw body
            for x, y in snake_positions[1:]:
                self.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=base_color, outline=''
                )
            # Draw head
            if snake_positions:
                x, y = snake_positions[0]
                self.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=head_color, outline=''
                )
        
        # Draw food
        food_x, food_y = self.food_pos
        self.create_oval(
            food_x * self.cell_size + 2, food_y * self.cell_size + 2,
            (food_x + 1) * self.cell_size - 2, (food_y + 1) * self.cell_size - 2,
            fill=self.config.FOOD_COLOR
        )
        
        # Draw scores
        self.create_text(
            50, 20,
            text=f'Green: {self.score1}',
            fill=self.config.SNAKE1_COLOR,
            font=self.config.SCORE_FONT
        )
        self.create_text(
            self.width - 50, 20,
            text=f'Orange: {self.score2}',
            fill=self.config.SNAKE2_COLOR,
            font=self.config.SCORE_FONT
        )

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
DirectionVector = Tuple[int, int]

class GameCanvas(tk.Canvas):
    def __init__(self, 
                 master: tk.Tk,
                 mode: GameMode,
                 config: GameConfig = None,
                 strategy1: Optional[Any] = None,
                 strategy2: Optional[Any] = None,
                 debug: Optional[DebugLogger] = None) -> None:
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
        
        self.score1 = 0
        self.score2 = 0
        
        self.directions: Dict[str, DirectionVector] = {
            'Up': (0, -1),
            'Down': (0, 1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }
        
        self._first_food = True
        
        self.reset_game()
        
        self.debug.log("Game canvas initialized")
        self.bind_all('<Key>', self.handle_keypress)
        self.update_game()

    def _place_food(self) -> Position:
        """Generate food position, with first food at grid center."""
        if self._first_food:
            x = self.grid_width // 2
            y = self.grid_height // 2
            
            while (x, y) in self.snake1 or (x, y) in self.snake2:
                x = random.randint(max(0, x-1), min(self.grid_width-1, x+1))
                y = random.randint(max(0, y-1), min(self.grid_height-1, y+1))
            
            self._first_food = False
            self.debug.log(f"Placed first food at central position: ({x}, {y})")
            return (x, y)
        
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake1 and (x, y) not in self.snake2:
                self.debug.log(f"Placed food at random position: ({x}, {y})")
                return (x, y)

    def reset_snake_position(self, snake_id: int) -> None:
        """Reset position of a specific snake while keeping the other snake and food unchanged."""
        if snake_id == 1:
            self.snake1 = [(2 - i, self.grid_height//2) for i in range(2)]  # Start with length 2 on left side
            self.direction1 = 'Right'
        else:
            self.snake2 = [(self.grid_width-3 + i, self.grid_height//2) for i in range(2)]  # Start with length 2 on right side
            self.direction2 = 'Left'
        self.debug.log(f"Reset position for snake {snake_id}")

    def reset_positions(self) -> None:
        """Reset both snake positions and place food."""
        self.snake1 = [(2 - i, self.grid_height//2) for i in range(2)]
        self.snake2 = [(self.grid_width-3 + i, self.grid_height//2) for i in range(2)]
        
        self._first_food = True
        self.food_pos = self._place_food()
        self.direction1 = 'Right'
        self.direction2 = 'Left'
        self.last_move_time = time.time()
        self.debug.log("All positions reset")

    def reset_game(self) -> None:
        """Reset entire game including scores."""
        self.debug.log("Resetting game")
        self.score1 = 0
        self.score2 = 0
        self.reset_positions()
        self.debug.log("Game reset complete")

    def handle_keypress(self, event: tk.Event) -> None:
        """Process keyboard input for game control."""
        key = event.keysym
        self.debug.log_key_press(key, self.direction1)
        
        if key == 'r':
            self.reset_game()
            return
        if key == 'Escape':
            self.master.destroy()
            return
        
        if self.mode == GameMode.PLAYER_VS_AI and key in self.directions:
            opposite = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}
            if key != opposite[self.direction1]:
                self.direction1 = key
                self.debug.log(f"Snake 1 direction changed to: {key}")

    def move_snake(self, positions: List[Position], direction: str, snake_id: int) -> Tuple[bool, List[Position]]:
        """Move snake and check for wall/self collisions."""
        dx, dy = self.directions[direction]
        new_head = (positions[0][0] + dx, positions[0][1] + dy)
        
        # Check wall collision
        if not (0 <= new_head[0] < self.grid_width and 0 <= new_head[1] < self.grid_height):
            self.debug.log_collision("wall", new_head)
            self.score2 += 1 if snake_id == 1 else 0
            self.score1 += 1 if snake_id == 2 else 0
            # Reset snake to initial position and length
            if snake_id == 1:
                self.snake1 = [(2 - i, self.grid_height//2) for i in range(2)]
                self.direction1 = 'Right'
                return False, self.snake1
            else:
                self.snake2 = [(self.grid_width-3 + i, self.grid_height//2) for i in range(2)]
                self.direction2 = 'Left'
                return False, self.snake2
        
        # Check self collision
        if new_head in positions[:-1]:
            self.debug.log(f"Snake {snake_id} self collision")
            self.score2 += 1 if snake_id == 1 else 0
            self.score1 += 1 if snake_id == 2 else 0
            self.reset_snake_position(snake_id)
            return False, positions if snake_id == 1 else self.snake2
        
        positions.insert(0, new_head)
        if new_head == self.food_pos:
            self.debug.log(f"Snake {snake_id} collected food")
            return True, positions
        
        positions.pop()
        return True, positions

    def check_snake_collisions(self) -> bool:
        """Check for collisions between snakes and handle consequences."""
        head1, head2 = self.snake1[0], self.snake2[0]
        collision_occurred = False
        
        # Check head-to-head collision
        if head1 == head2:
            self.debug.log("Head to head collision - resetting both snake positions")
            self.reset_snake_position(1)
            self.reset_snake_position(2)
            return True
        
        # Check if snake 1's head hits snake 2's body
        if head1 in self.snake2[1:]:
            self.debug.log("Snake 1 hit Snake 2's body")
            self.score2 += 1
            self.reset_snake_position(1)
            collision_occurred = True
        
        # Check if snake 2's head hits snake 1's body
        if head2 in self.snake1[1:]:
            self.debug.log("Snake 2 hit Snake 1's body")
            self.score1 += 1
            self.reset_snake_position(2)
            collision_occurred = True
        
        return collision_occurred

    def update_game(self) -> None:
        """Update game state and redraw."""
        current_time = time.time()
        if current_time - self.last_move_time >= 0.1:
            if self.mode == GameMode.AI_VS_AI:
                state = self._get_game_state()
                if self.strategy1:
                    next_move = self.strategy1.get_next_move(state, 1)
                    self.direction1 = next_move.name.capitalize()
                if self.strategy2:
                    next_move = self.strategy2.get_next_move(state, 2)
                    self.direction2 = next_move.name.capitalize()
            elif self.mode == GameMode.PLAYER_VS_AI and self.strategy2:
                state = self._get_game_state()
                next_move = self.strategy2.get_next_move(state, 2)
                self.direction2 = next_move.name.capitalize()

            # Move snakes and check individual collisions
            _, self.snake1 = self.move_snake(self.snake1, self.direction1, 1)
            _, self.snake2 = self.move_snake(self.snake2, self.direction2, 2)
            
            # Check snake-to-snake collisions
            self.check_snake_collisions()
            
            # Check for food collection
            for snake_pos, snake_num in [(self.snake1[0], 1), (self.snake2[0], 2)]:
                if snake_pos == self.food_pos:
                    if snake_num == 1:
                        self.score1 += 1
                        self.debug.log(f"Snake 1 score: {self.score1}")
                    else:
                        self.score2 += 1
                        self.debug.log(f"Snake 2 score: {self.score2}")
                    self.food_pos = self._place_food()
            
            self.last_move_time = current_time
        
        self.draw_game()
        self.after(16, self.update_game)

    def _get_game_state(self) -> GameState:
        """Create current game state for AI decision making."""
        return GameState(
            snake1=self.snake1.copy(),
            snake2=self.snake2.copy(),
            food_position=self.food_pos,
            grid_width=self.grid_width,
            grid_height=self.grid_height,
            score1=self.score1,
            score2=self.score2
        )

    def draw_game(self) -> None:
        """Render current game state."""
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

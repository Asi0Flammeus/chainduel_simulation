from __future__ import annotations
import tkinter as tk
from typing import Tuple, Optional, List, Dict, Any
import time
import random
from src.utils.debug import DebugLogger
from src.common.enums import GameMode, Direction
from src.common.types import GameState

Position = Tuple[int, int]
DirectionVector = Tuple[int, int]

class GameCanvas(tk.Canvas):
    """A canvas widget that displays and manages the snake game.
    
    Handles game rendering, state management, collision detection,
    and user input processing for a two-snake game environment.
    
    Attributes:
        width (int): Canvas width in pixels
        height (int): Canvas height in pixels
        cell_size (int): Size of each grid cell in pixels
        grid_width (int): Number of cells horizontally
        grid_height (int): Number of cells vertically
        score1 (int): Score of snake 1 (green)
        score2 (int): Score of snake 2 (orange)
    """
    
    def __init__(self, 
                 master: tk.Tk,
                 mode: GameMode,
                 config: Any,
                 strategy1: Optional[Any],
                 strategy2: Optional[Any],
                 debug: Optional[DebugLogger] = None) -> None:
        """Initialize the game canvas and state."""
        super().__init__(
            master,
            width=config.WINDOW_WIDTH,
            height=config.WINDOW_HEIGHT,
            bg='black',
            highlightthickness=0
        )
        
        self.debug = debug or DebugLogger(False)
        self.mode = mode
        self.strategy1 = strategy1
        self.strategy2 = strategy2
        
        self.width = config.WINDOW_WIDTH
        self.height = config.WINDOW_HEIGHT
        self.cell_size = config.GRID_SIZE
        self.grid_width = self.width // self.cell_size
        self.grid_height = self.height // self.cell_size
        
        self.score1 = 0
        self.score2 = 0
        
        self.directions: Dict[str, DirectionVector] = {
            'Up': (0, -1),
            'Down': (0, 1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }
        
        self.reset_positions()
        
        self.debug.log("Game canvas initialized")
        self.bind_all('<Key>', self.handle_keypress)
        self.update_game()
    
    def _place_food(self) -> Position:
        """Generate new random food position not overlapping with snakes."""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake1 and (x, y) not in self.snake2:
                self.debug.log(f"Placed food at position: ({x}, {y})")
                return (x, y)
    
    def reset_positions(self) -> None:
        """Reset snake positions and place food randomly for next point."""
        self.debug.log("Resetting positions for next point")
        # Reset snake positions but maintain current lengths
        # Extend bodies to the left/right of starting positions based on current lengths
        self.snake1 = [(2 - i, self.grid_height//2) for i in range(2)]  # Start with length 2
        self.snake2 = [(self.grid_width-3 + i, self.grid_height//2) for i in range(2)]  # Start with length 2
        self.food_pos = self._place_food()
        self.direction1 = 'Right'
        self.direction2 = 'Left'
        self.last_move_time = time.time()
        self.debug.log("Position reset complete")
    
    def reset_game(self) -> None:
        """Reset entire game including scores."""
        self.debug.log("Resetting game")
        self.score1 = 0
        self.score2 = 0
        self.reset_positions()
        self.debug.log("Game reset complete")
    
    def handle_keypress(self, event: tk.Event) -> None:
        """Process keyboard input for game control and snake movement."""
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
        """Move snake in specified direction and handle collisions/growth."""
        dx, dy = self.directions[direction]
        new_head = (positions[0][0] + dx, positions[0][1] + dy)
        
        if not (0 <= new_head[0] < self.grid_width and 0 <= new_head[1] < self.grid_height):
            self.debug.log_collision("wall", new_head)
            if snake_id == 1:
                self.score2 += 1
                self.debug.log(f"Point awarded to Snake 2 for wall collision")
            else:
                self.score1 += 1
                self.debug.log(f"Point awarded to Snake 1 for wall collision")
            return False, positions
        
        positions.insert(0, new_head)
        if new_head == self.food_pos:
            self.debug.log(f"Snake {snake_id} collected food")
            return True, positions  # Snake grows by keeping tail
        
        positions.pop()  # Remove tail if not growing
        return True, positions
    
    def check_collision(self) -> bool:
        """Check for collisions between snakes and update scores accordingly.
        
        Returns True if any collision occurred, with points awarded based on:
        - Self collision: Point to opponent, reset length of colliding snake
        - Head to body collision: Point to snake whose body was hit, reset length of colliding snake
        - Head to head collision: No points awarded, reset length of both snakes
        """
        head1, head2 = self.snake1[0], self.snake2[0]
        collision_occurred = False
        
        # Check head-to-head collision first
        if head1 == head2:
            self.debug.log("Head to head collision - resetting both snakes")
            self.snake1 = self.snake1[:2]  # Reset to initial length
            self.snake2 = self.snake2[:2]  # Reset to initial length
            return True
            
        # Check self-collisions
        if head1 in self.snake1[1:]:
            self.score2 += 1
            self.snake1 = self.snake1[:2]  # Reset length of snake 1
            self.debug.log("Point awarded to Snake 2 for Snake 1 self-collision")
            collision_occurred = True
            
        if head2 in self.snake2[1:]:
            self.score1 += 1
            self.snake2 = self.snake2[:2]  # Reset length of snake 2
            self.debug.log("Point awarded to Snake 1 for Snake 2 self-collision")
            collision_occurred = True
        
        # Check head-to-body collisions
        if head1 in self.snake2[1:]:  # Snake 1's head hits Snake 2's body
            self.score2 += 1
            self.snake1 = self.snake1[:2]  # Reset length of snake 1
            self.debug.log("Point awarded to Snake 2 - Snake 1 hit Snake 2's body")
            collision_occurred = True
            
        if head2 in self.snake1[1:]:  # Snake 2's head hits Snake 1's body
            self.score1 += 1
            self.snake2 = self.snake2[:2]  # Reset length of snake 2
            self.debug.log("Point awarded to Snake 1 - Snake 2 hit Snake 1's body")
            collision_occurred = True
            
        return collision_occurred
    
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
    
    def update_game(self) -> None:
        """Update game state and trigger redraw."""
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

            valid1, self.snake1 = self.move_snake(self.snake1, self.direction1, 1)
            valid2, self.snake2 = self.move_snake(self.snake2, self.direction2, 2)
            
            if not valid1 or not valid2 or self.check_collision():
                self.reset_positions()
            
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
    
    def draw_game(self) -> None:
        """Render current game state to the canvas."""
        self.delete('all')
        
        # Draw grid
        for i in range(0, self.width + 1, self.cell_size):
            self.create_line(i, 0, i, self.height, fill='#333333')
        for i in range(0, self.height + 1, self.cell_size):
            self.create_line(0, i, self.width, i, fill='#333333')
        
        # Draw snakes with darker heads
        for snake_positions, head_color, base_color in [
            (self.snake1, '#2ecc71', '#164a29'),  # Green snake with darker green head
            (self.snake2, '#e67e22', '#a65602')   # Orange snake with darker orange head
        ]:
            # Draw body
            for x, y in snake_positions[1:]:
                self.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=base_color, outline=''
                )
            # Draw head (first position) in darker color
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
            fill='yellow'
        )
        
        # Draw scores
        self.create_text(
            50, 20,
            text=f'Green: {self.score1}',
            fill='#2ecc71',
            font=('Arial', 16, 'bold')
        )
        self.create_text(
            self.width - 50, 20,
            text=f'Orange: {self.score2}',
            fill='#e67e22',
            font=('Arial', 16, 'bold')
        )

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
        game_active (bool): Whether game is currently running
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
        """Initialize the game canvas and state.
        
        Args:
            master: Parent tkinter window
            mode: Game mode (PLAYER_VS_AI or AI_VS_AI)
            config: Game configuration object
            strategy1: AI strategy for snake 1 (None if player controlled)
            strategy2: AI strategy for snake 2
            debug: Debug logger instance
        """
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
        
        self.snake1 = [(2, self.grid_height//2), (1, self.grid_height//2)]
        self.snake2 = [(self.grid_width-3, self.grid_height//2), (self.grid_width-2, self.grid_height//2)]
        self.food_pos = self._place_food()
        self.score1 = 0
        self.score2 = 0
        
        self.direction1 = 'Right'
        self.direction2 = 'Left'
        self.last_move_time = time.time()
        self.game_active = True
        
        self.directions: Dict[str, DirectionVector] = {
            'Up': (0, -1),
            'Down': (0, 1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }
        
        self.debug.log("Game canvas initialized")
        self.debug.log_snake_state(1, self.snake1, self.direction1)
        self.debug.log_snake_state(2, self.snake2, self.direction2)
        
        self.bind_all('<Key>', self.handle_keypress)
        self.update_game()
    
    def _place_food(self) -> Position:
        """Generate new food position not overlapping with snakes."""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake1 and (x, y) not in self.snake2:
                self.debug.log(f"Placed food at position: ({x}, {y})")
                return (x, y)
    
    def handle_keypress(self, event: tk.Event) -> None:
        """Process keyboard input for game control and snake movement."""
        key = event.keysym
        self.debug.log_key_press(key, self.direction1)
        
        if key == 'r':
            self.debug.log("Game reset triggered")
            self.reset_game()
            return
        if key == 'Escape':
            self.debug.log("Game quit triggered")
            self.master.destroy()
            return
        
        if self.mode == GameMode.PLAYER_VS_AI and key in self.directions:
            opposite = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}
            if key != opposite[self.direction1]:
                self.direction1 = key
                self.debug.log(f"Snake 1 direction changed to: {key}")
    
    def move_snake(self, positions: List[Position], direction: str, snake_id: int) -> Tuple[bool, List[Position]]:
        """Move snake in specified direction and handle collisions/growth.
        
        Args:
            positions: Current snake positions
            direction: Movement direction
            snake_id: Identifier of the snake (1 or 2)
            
        Returns:
            Tuple of (valid_move, new_positions)
        """
        dx, dy = self.directions[direction]
        new_head = (positions[0][0] + dx, positions[0][1] + dy)
        
        if not (0 <= new_head[0] < self.grid_width and 0 <= new_head[1] < self.grid_height):
            self.debug.log_collision("wall", new_head)
            return False, positions
        
        positions.insert(0, new_head)
        if new_head == self.food_pos:
            self.debug.log(f"Snake {snake_id} collected food")
            return True, positions
        
        positions.pop()
        return True, positions
    
    def check_collision(self) -> bool:
        """Check for collisions between snakes or self-collisions."""
        head1, head2 = self.snake1[0], self.snake2[0]
        
        for head, snake in [(head1, self.snake1[1:]), (head1, self.snake2),
                          (head2, self.snake2[1:]), (head2, self.snake1)]:
            if head in snake:
                self.debug.log_collision("collision", head)
                return True
        return False
    
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
        if self.game_active:
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
                
                self.debug.log_snake_state(1, self.snake1, self.direction1)
                self.debug.log_snake_state(2, self.snake2, self.direction2)
                
                if not valid1 or not valid2 or self.check_collision():
                    self.debug.log("Game over")
                    self.game_active = False
                
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
        
        for i in range(0, self.width + 1, self.cell_size):
            self.create_line(i, 0, i, self.height, fill='#333333')
        for i in range(0, self.height + 1, self.cell_size):
            self.create_line(0, i, self.width, i, fill='#333333')
        
        for snake_positions, color in [(self.snake1, '#2ecc71'), (self.snake2, '#e67e22')]:
            for x, y in snake_positions:
                self.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=color, outline=''
                )
        
        food_x, food_y = self.food_pos
        self.create_oval(
            food_x * self.cell_size + 2, food_y * self.cell_size + 2,
            (food_x + 1) * self.cell_size - 2, (food_y + 1) * self.cell_size - 2,
            fill='yellow'
        )
        
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
        
        if not self.game_active:
            self.create_text(
                self.width/2, self.height/2,
                text='GAME OVER\nPress R to restart',
                fill='white',
                font=('Arial', 24, 'bold'),
                justify='center'
            )
    
    def reset_game(self) -> None:
        """Reset game to initial state."""
        self.debug.log("Resetting game")
        self.snake1 = [(2, self.grid_height//2), (1, self.grid_height//2)]
        self.snake2 = [(self.grid_width-3, self.grid_height//2), (self.grid_width-2, self.grid_height//2)]
        self.food_pos = self._place_food()
        self.score1 = 0
        self.score2 = 0
        self.direction1 = 'Right'
        self.direction2 = 'Left'
        self.game_active = True
        self.debug.log("Game reset complete")

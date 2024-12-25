import tkinter as tk
from typing import Tuple, Optional, List
import time
import random

class GameCanvas(tk.Canvas):
    def __init__(self, master: tk.Tk, width: int = 800, height: int = 600, cell_size: int = 20):
        # Initialize the canvas
        super().__init__(
            master,
            width=width,
            height=height,
            bg='black',
            highlightthickness=0
        )
        
        # Game dimensions
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size
        
        # Game state
        self.snake1 = [(2, self.grid_height//2)]
        self.snake2 = [(self.grid_width-3, self.grid_height//2)]
        self.food_pos = self._place_food()
        self.score1 = 0
        self.score2 = 0
        
        # Movement state
        self.direction1 = 'Right'  # Default direction for snake 1
        self.direction2 = 'Left'   # Default direction for snake 2
        self.last_move_time = time.time()
        self.game_active = True
        
        # Movement mappings
        self.directions = {
            'Up': (0, -1),
            'Down': (0, 1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }
        
        # Bind keys
        self.bind_all('<Key>', self.handle_keypress)
        
        # Start game loop
        self.update_game()
    
    def _place_food(self) -> Tuple[int, int]:
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake1 and (x, y) not in self.snake2:
                return (x, y)
    
    def handle_keypress(self, event):
        key = event.keysym
        
        if key == 'r':
            self.reset_game()
            return
        if key == 'Escape':
            self.master.destroy()
            return
        
        # Player movement (Snake 1)
        if key in ['Up', 'Down', 'Left', 'Right']:
            current = self.direction1
            opposite = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}
            if key != opposite[current]:
                self.direction1 = key
    
    def move_snake(self, positions: List[Tuple[int, int]], direction: str) -> Tuple[bool, List[Tuple[int, int]]]:
        dx, dy = self.directions[direction]
        new_head = (positions[0][0] + dx, positions[0][1] + dy)
        
        # Check wall collision
        if not (0 <= new_head[0] < self.grid_width and 0 <= new_head[1] < self.grid_height):
            return False, positions
        
        # Move snake
        positions.insert(0, new_head)
        if new_head == self.food_pos:
            return True, positions  # Snake grows
        else:
            positions.pop()  # Remove tail
            return True, positions
    
    def check_collision(self) -> bool:
        head1 = self.snake1[0]
        head2 = self.snake2[0]
        
        # Check snake collisions with each other and themselves
        if (head1 in self.snake1[1:] or 
            head1 in self.snake2 or 
            head2 in self.snake2[1:] or 
            head2 in self.snake1):
            return True
        
        return False
    
    def update_game(self):
        if self.game_active:
            current_time = time.time()
            if current_time - self.last_move_time >= 0.1:  # Move every 100ms
                # Move snakes
                valid1, self.snake1 = self.move_snake(self.snake1, self.direction1)
                valid2, self.snake2 = self.move_snake(self.snake2, self.direction2)
                
                # Check collisions
                if not valid1 or not valid2 or self.check_collision():
                    self.game_active = False
                
                # Check food collection
                if self.snake1[0] == self.food_pos:
                    self.score1 += 1
                    self.food_pos = self._place_food()
                elif self.snake2[0] == self.food_pos:
                    self.score2 += 1
                    self.food_pos = self._place_food()
                
                self.last_move_time = current_time
        
        self.draw_game()
        self.after(16, self.update_game)  # Update at ~60 FPS
    
    def draw_game(self):
        self.delete('all')
        
        # Draw grid
        for i in range(0, self.width + 1, self.cell_size):
            self.create_line(i, 0, i, self.height, fill='#333333')
        for i in range(0, self.height + 1, self.cell_size):
            self.create_line(0, i, self.width, i, fill='#333333')
        
        # Draw snakes
        for x, y in self.snake1:
            self.create_rectangle(
                x * self.cell_size, y * self.cell_size,
                (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                fill='#2ecc71', outline=''  # Green
            )
        for x, y in self.snake2:
            self.create_rectangle(
                x * self.cell_size, y * self.cell_size,
                (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                fill='#e67e22', outline=''  # Orange
            )
        
        # Draw food
        x, y = self.food_pos
        self.create_oval(
            x * self.cell_size + 2, y * self.cell_size + 2,
            (x + 1) * self.cell_size - 2, (y + 1) * self.cell_size - 2,
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
        
        if not self.game_active:
            self.create_text(
                self.width/2, self.height/2,
                text='GAME OVER\nPress R to restart',
                fill='white',
                font=('Arial', 24, 'bold'),
                justify='center'
            )
    
    def reset_game(self):
        self.snake1 = [(2, self.grid_height//2)]
        self.snake2 = [(self.grid_width-3, self.grid_height//2)]
        self.food_pos = self._place_food()
        self.score1 = 0
        self.score2 = 0
        self.direction1 = 'Right'
        self.direction2 = 'Left'
        self.game_active = True

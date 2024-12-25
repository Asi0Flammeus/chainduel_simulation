# src/core/snake.py
from typing import List, Tuple, Optional
from ..common.enums import Direction

class Snake:
    def __init__(self, initial_positions: List[Tuple[int, int]], initial_direction: Optional[Direction] = None):
        self.body = initial_positions
        self.direction = initial_direction
        self.next_direction = initial_direction
        self.growing = False
    
    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]
    
    @property
    def length(self) -> int:
        return len(self.body)
    
    def set_direction(self, new_direction: Direction) -> bool:
        """
        Set new direction if it's valid (not opposite to current direction)
        Returns True if direction was changed
        """
        if self.direction is None:
            self.direction = new_direction
            self.next_direction = new_direction
            return True
            
        # Can't reverse direction
        if (self.direction == Direction.UP and new_direction == Direction.DOWN or
            self.direction == Direction.DOWN and new_direction == Direction.UP or
            self.direction == Direction.LEFT and new_direction == Direction.RIGHT or
            self.direction == Direction.RIGHT and new_direction == Direction.LEFT):
            return False
            
        self.next_direction = new_direction
        return True
    
    def move(self, grid_width: int, grid_height: int) -> bool:
        """
        Move snake in its current direction.
        Returns False if move would cause wall collision
        """
        if self.direction is None or self.next_direction is None:
            return True
            
        # Update current direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.head
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Check wall collision
        if not (0 <= new_head[0] < grid_width and 0 <= new_head[1] < grid_height):
            return False
            
        # Add new head
        self.body.insert(0, new_head)
        
        # Remove tail if not growing
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False
            
        return True
    
    def check_collision(self, other_snake: 'Snake') -> bool:
        """
        Check if this snake has collided with another snake
        """
        # Check collision with self (excluding head)
        if self.head in self.body[1:]:
            return True
            
        # Check collision with other snake
        if self.head in other_snake.body:
            return True
            
        return False
    
    def will_collide(self, position: Tuple[int, int]) -> bool:
        """
        Check if moving to a position would cause collision
        """
        return position in self.body
    
    def grow(self):
        """
        Mark snake to grow on next move
        """
        self.growing = True
    
    def copy(self) -> 'Snake':
        """
        Create a deep copy of the snake
        """
        new_snake = Snake(self.body.copy(), self.direction)
        new_snake.next_direction = self.next_direction
        new_snake.growing = self.growing
        return new_snake

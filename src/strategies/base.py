# src/strategies/base.py
from abc import ABC, abstractmethod
from ..common.enums import Direction
from ..common.types import GameState

class SnakeStrategy(ABC):
    """Base class for all snake movement strategies."""
    
    @abstractmethod
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        """
        Determine the next move for the snake.
        
        Args:
            state (GameState): Current state of the game
            snake_id (int): ID of the snake (1 or 2)
            
        Returns:
            Direction: The direction to move in
        """
        pass

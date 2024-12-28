# src/core/game_state.py
from dataclasses import dataclass
from typing import List, Tuple, Optional
from ..common.enums import Direction

@dataclass
class GameState:
    snake1: List[Tuple[int, int]]
    snake2: List[Tuple[int, int]]
    food_position: Tuple[int, int]
    grid_width: int
    grid_height: int
    score1: int = 50000  # Starting score
    score2: int = 50000  # Starting score
    direction1: Optional[Direction] = None
    direction2: Optional[Direction] = None
    next_direction1: Optional[Direction] = None
    next_direction2: Optional[Direction] = None
    game_active: bool = True
    
    @property
    def is_game_over(self) -> bool:
        return self.score1 >= 100000 or self.score2 >= 100000

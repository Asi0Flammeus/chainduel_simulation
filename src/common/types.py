from dataclasses import dataclass
from typing import List, Tuple, Optional
from .enums import Direction

@dataclass
class GameState:
    snake1: List[Tuple[int, int]]
    snake2: List[Tuple[int, int]]
    food_position: Tuple[int, int]
    grid_width: int
    grid_height: int
    score1: int = 0
    score2: int = 0
    direction1: Optional[Direction] = None
    direction2: Optional[Direction] = None
    next_direction1: Optional[Direction] = None
    next_direction2: Optional[Direction] = None
    game_active: bool = True

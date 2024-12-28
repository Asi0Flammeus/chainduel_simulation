# src/common/constants.py
from dataclasses import dataclass

@dataclass
class GameConfig:
    # Window settings
    WINDOW_WIDTH: int = 1020  # 51 * 20
    WINDOW_HEIGHT: int = 500  # 25 * 20 + score bar
    GRID_SIZE: int = 20
    
    # Game settings
    FPS: int = 15
    INITIAL_SNAKE_LENGTH: int = 2
    STARTING_SCORE: int = 50000
    WINNING_SCORE: int = 100000
    SCORE_BAR_HEIGHT: int = 30
    
    # Colors
    GRID_COLOR: str = '#333333'
    SNAKE1_COLOR: str = '#2ecc71'  # Green
    SNAKE2_COLOR: str = '#e67e22'  # Orange
    SCORE_BAR_BG: str = '#444444'
    SCORE_BAR1_COLOR: str = '#1a8045'  # Darker green
    SCORE_BAR2_COLOR: str = '#b35c00'  # Darker orange
    FOOD_COLOR: str = 'yellow'
    BACKGROUND_COLOR: str = 'black'
    TEXT_COLOR: str = 'white'
    
    # Font settings
    SCORE_FONT: tuple = ('Arial', 16, 'bold')
    GAMEOVER_FONT: tuple = ('Arial', 24, 'bold')
    
    @property
    def GRID_WIDTH(self) -> int:
        return 51
    
    @property
    def GRID_HEIGHT(self) -> int:
        return 25
        
    def calculate_points(self, snake_length: int) -> int:
        """Calculate points based on snake length: 2000 * 2^(L-2)"""
        return int(2000 * (2 ** (snake_length - 2)))

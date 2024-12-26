from dataclasses import dataclass

@dataclass
class GameConfig:
    # Window settings
    WINDOW_WIDTH: int = 1020  # 51 * 20
    WINDOW_HEIGHT: int = 500  # 25 * 20
    GRID_SIZE: int = 20
    
    # Game settings
    FPS: int = 15
    INITIAL_SNAKE_LENGTH: int = 2
    MAX_SCORE: int = 21
    
    # Colors
    GRID_COLOR: str = '#333333'
    SNAKE1_COLOR: str = '#2ecc71'  # Green
    SNAKE2_COLOR: str = '#e67e22'  # Orange
    FOOD_COLOR: str = 'yellow'
    BACKGROUND_COLOR: str = 'black'
    TEXT_COLOR: str = 'white'
    
    # Font settings
    SCORE_FONT: tuple = ('Arial', 16, 'bold')
    GAMEOVER_FONT: tuple = ('Arial', 24, 'bold')
    
    @property
    def GRID_WIDTH(self) -> int:
        return 51  # Explicitly set to 51
    
    @property
    def GRID_HEIGHT(self) -> int:
        return 25  # Explicitly set to 25

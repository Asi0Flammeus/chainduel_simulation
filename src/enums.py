from enum import Enum, auto

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @classmethod
    def opposite(cls, direction: 'Direction') -> 'Direction':
        if direction == cls.UP: return cls.DOWN
        if direction == cls.DOWN: return cls.UP
        if direction == cls.LEFT: return cls.RIGHT
        if direction == cls.RIGHT: return cls.LEFT


class GameMode(Enum):
    PLAYER_VS_AI = "Player vs AI"
    AI_VS_AI = "AI vs AI"
    SIMULATION = "Simulation"


class Strategy(Enum):
    RANDOM = "Random Movement"
    FOOD_SEEKING = "Food Seeking"
    ANTICIPATION = "Anticipation"

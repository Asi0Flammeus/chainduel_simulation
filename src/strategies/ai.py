from __future__ import annotations
import random
import math
from typing import List, Tuple, Dict, Optional
from collections import deque
from enum import Enum

from ..common.enums import Direction
from ..common.types import GameState
from .base import SnakeStrategy

class MovementHistory:
    """Tracks recent movements to prevent oscillations."""
    def __init__(self, size: int = 4):
        self.history = deque(maxlen=size)
        
    def add_move(self, direction: Direction):
        self.history.append(direction)
        
    def would_oscillate(self, next_direction: Direction) -> bool:
        """Check if adding this move would create an oscillation pattern."""
        if not self.history:  # Empty history
            return False
            
        # Check for immediate reversal
        if len(self.history) > 0 and Direction.opposite(self.history[-1]) == next_direction:
            return True
            
        # Create temporary history with the new move
        temp_history = list(self.history)
        temp_history.append(next_direction)
        if len(temp_history) >= 4:
            # Check for UDUD or LRLR patterns
            last_four = temp_history[-4:]
            if (last_four[0] == last_four[2] and 
                last_four[1] == last_four[3] and 
                Direction.opposite(last_four[0]) == last_four[1]):
                return True
        return False
    
    def get_last_move(self) -> Optional[Direction]:
        """Safely get the last move from history."""
        return self.history[-1] if len(self.history) > 0 else None

class SimpleFoodSeekingStrategy(SnakeStrategy):
    """A basic strategy that simply moves towards the food."""

    def __init__(self):
        self.movement_history = MovementHistory()

    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position

        # Calculate distances to food in each direction
        distances = {}
        for direction in Direction:
            new_x, new_y = head_x + direction.value[0], head_y + direction.value[1]

            # Check for boundaries and collisions
            if not (0 <= new_x < state.grid_width and 0 <= new_y < state.grid_height):
                continue
            if (new_x, new_y) in snake[:-1]:
                continue
            
            distances[direction] = abs(new_x - food_x) + abs(new_y - food_y)

        # Choose the direction with the shortest distance to food
        if distances:
            best_direction = min(distances, key=distances.get)
            self.movement_history.add_move(best_direction)
            return best_direction
        else:
            # If no safe moves, choose a random direction
            possible_moves = []
            for direction in Direction:
                new_x, new_y = head_x + direction.value[0], head_y + direction.value[1]
                if (0 <= new_x < state.grid_width and 0 <= new_y < state.grid_height) and (new_x, new_y) not in snake[:-1]:
                    possible_moves.append(direction)
            if possible_moves:
                direction = random.choice(possible_moves)
                self.movement_history.add_move(direction)
                return direction
            else:
                return random.choice(list(Direction))

class AdaptiveSeekingStrategy(SnakeStrategy):
    """A strategy that seeks food while trying to maximize space on either side."""

    def __init__(self):
        self.movement_history = MovementHistory()

    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position

        # Calculate scores for each direction
        scores = {}
        for direction in Direction:
            new_x, new_y = head_x + direction.value[0], head_y + direction.value[1]

            # Check for boundaries and collisions
            if not (0 <= new_x < state.grid_width and 0 <= new_y < state.grid_height):
                continue
            if (new_x, new_y) in snake[:-1]:
                continue

            # Calculate distance to food
            distance_to_food = abs(new_x - food_x) + abs(new_y - food_y)

            # Calculate space score (favoring the side with more space)
            left_space = new_x
            right_space = state.grid_width - 1 - new_x
            space_score = max(left_space, right_space)

            # Adjust space score based on food position
            if food_x < state.grid_width // 2:  # Food is on the left
                space_score = left_space
            else:  # Food is on the right
                space_score = right_space

            # Combine scores (prioritize food, then space)
            scores[direction] = -distance_to_food + space_score * 0.5

        # Choose the direction with the highest score
        if scores:
            best_direction = max(scores, key=scores.get)
            self.movement_history.add_move(best_direction)
            return best_direction
        else:
            # If no safe moves, choose a random direction
            possible_moves = []
            for direction in Direction:
                new_x, new_y = head_x + direction.value[0], head_y + direction.value[1]
                if (0 <= new_x < state.grid_width and 0 <= new_y < state.grid_height) and (new_x, new_y) not in snake[:-1]:
                    possible_moves.append(direction)
            if possible_moves:
                direction = random.choice(possible_moves)
                self.movement_history.add_move(direction)
                return direction
            else:
                return random.choice(list(Direction))

class AggressiveStrategy(SnakeStrategy):
    """An aggressive strategy that prioritizes attacking the opponent."""

    def __init__(self):
        self.movement_history = MovementHistory()

    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        opp_x, opp_y = opponent[0]

        # Calculate scores for each direction
        scores = {}
        for direction in Direction:
            new_x, new_y = head_x + direction.value[0], head_y + direction.value[1]

            # Check for boundaries and collisions
            if not (0 <= new_x < state.grid_width and 0 <= new_y < state.grid_height):
                continue
            if (new_x, new_y) in snake[:-1]:
                continue

            # Calculate distance to opponent's head
            distance_to_opponent = abs(new_x - opp_x) + abs(new_y - opp_y)

            # Prioritize moves that bring us closer to the opponent
            scores[direction] = -distance_to_opponent

        # Choose the direction with the highest score
        if scores:
            best_direction = max(scores, key=scores.get)
            self.movement_history.add_move(best_direction)
            return best_direction
        else:
            # If no safe moves, choose a random direction
            possible_moves = []
            for direction in Direction:
                new_x, new_y = head_x + direction.value[0], head_y + direction.value[1]
                if (0 <= new_x < state.grid_width and 0 <= new_y < state.grid_height) and (new_x, new_y) not in snake[:-1]:
                    possible_moves.append(direction)
            if possible_moves:
                direction = random.choice(possible_moves)
                self.movement_history.add_move(direction)
                return direction
            else:
                return random.choice(list(Direction))

class NoisyAdaptiveStrategy(SnakeStrategy):
    """An adaptive strategy with a small chance of random movement."""

    def __init__(self, noise_level: float = 0.01):
        self.movement_history = MovementHistory()
        self.noise_level = noise_level

    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position

        # Add a small chance of random movement
        if random.random() < self.noise_level:
            possible_moves = []
            for direction in Direction:
                new_x, new_y = head_x + direction.value[0], head_y + direction.value[1]
                if (0 <= new_x < state.grid_width and 0 <= new_y < state.grid_height) and (new_x, new_y) not in snake[:-1]:
                    possible_moves.append(direction)
            if possible_moves:
                direction = random.choice(possible_moves)
                self.movement_history.add_move(direction)
                return direction
            else:
                return random.choice(list(Direction))

        # Calculate scores for each direction
        scores = {}
        for direction in Direction:
            new_x, new_y = head_x + direction.value[0], head_y + direction.value[1]

            # Check for boundaries and collisions
            if not (0 <= new_x < state.grid_width and 0 <= new_y < state.grid_height):
                continue
            if (new_x, new_y) in snake[:-1]:
                continue

            # Calculate distance to food
            distance_to_food = abs(new_x - food_x) + abs(new_y - food_y)

            # Combine scores
            scores[direction] = -distance_to_food

        # Choose the direction with the highest score
        if scores:
            best_direction = max(scores, key=scores.get)
            self.movement_history.add_move(best_direction)
            return best_direction
        else:
            # If no safe moves, choose a random direction
            possible_moves = []
            for direction in Direction:
                new_x, new_y = head_x + direction.value[0], head_y + direction.value[1]
                if (0 <= new_x < state.grid_width and 0 <= new_y < state.grid_height) and (new_x, new_y) not in snake[:-1]:
                    possible_moves.append(direction)
            if possible_moves:
                direction = random.choice(possible_moves)
                self.movement_history.add_move(direction)
                return direction
            else:
                return random.choice(list(Direction))


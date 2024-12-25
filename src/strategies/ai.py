# src/strategies/ai.py
import random
import math
from typing import List, Tuple

from ..common.enums import Direction
from ..common.types import GameState
from .base import SnakeStrategy
from ..core.snake import Snake

class RandomStrategy(SnakeStrategy):
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        """Simple strategy that makes random valid moves."""
        return random.choice(list(Direction))


class FoodSeekingStrategy(SnakeStrategy):
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        """Strategy that seeks the nearest path to food while avoiding collisions."""
        # Get the relevant snake and its positions
        snake = state.snake1 if snake_id == 1 else state.snake2
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        
        possible_moves: List[Tuple[float, Direction]] = []
        
        # Check all possible moves
        for direction in Direction:
            new_x = head_x + direction.value[0]
            new_y = head_y + direction.value[1]
            
            # Check if move is valid (within bounds and no collision)
            if (0 <= new_x < state.grid_width and 
                0 <= new_y < state.grid_height and 
                (new_x, new_y) not in snake):
                
                # Calculate Manhattan distance to food
                dist = abs(food_x - new_x) + abs(food_y - new_y)
                possible_moves.append((dist, direction))
        
        # Choose the move that gets us closest to food, or random if no valid moves
        if possible_moves:
            return min(possible_moves, key=lambda x: x[0])[1]
        return random.choice(list(Direction))


class AnticipationStrategy(SnakeStrategy):
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        """
        Advanced strategy that considers opponent's position and anticipates moves.
        If opponent is closer to food, tries to cut them off by moving to the opposite side.
        """
        # Get the relevant snake and opponent positions
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        opp_x, opp_y = opponent[0]
        food_x, food_y = state.food_position
        
        # Calculate Euclidean distances to food
        my_food_dist = math.sqrt((food_x - head_x)**2 + (food_y - head_y)**2)
        opp_food_dist = math.sqrt((food_x - opp_x)**2 + (food_y - opp_y)**2)
        
        # Choose target position based on distances
        if my_food_dist > opp_food_dist:
            # If opponent is closer, try to cut them off
            target_x = food_x + (food_x - opp_x)
            target_y = food_y + (food_y - opp_y)
            # Ensure target stays within grid bounds
            target_x = max(0, min(target_x, state.grid_width - 1))
            target_y = max(0, min(target_y, state.grid_height - 1))
        else:
            # If we're closer, go straight for the food
            target_x, target_y = food_x, food_y
        
        possible_moves: List[Tuple[float, Direction]] = []
        
        # Evaluate all possible moves
        for direction in Direction:
            new_x = head_x + direction.value[0]
            new_y = head_y + direction.value[1]
            
            # Check if move is valid (within bounds and no collision)
            if (0 <= new_x < state.grid_width and 
                0 <= new_y < state.grid_height and 
                (new_x, new_y) not in snake):
                
                # Calculate Manhattan distance to target
                dist = abs(target_x - new_x) + abs(target_y - new_y)
                possible_moves.append((dist, direction))
        
        # Choose the move that gets us closest to target, or random if no valid moves
        if possible_moves:
            return min(possible_moves, key=lambda x: x[0])[1]
        return random.choice(list(Direction))

from __future__ import annotations
import random
import math
from typing import List, Tuple, Dict

from ..common.enums import Direction
from ..common.types import GameState
from .base import SnakeStrategy

def predict_next_position(pos: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
    """Calculate next grid position given current position and movement direction."""
    return (pos[0] + direction.value[0], pos[1] + direction.value[1])

def is_safe_move(state: GameState, snake_id: int, next_pos: Tuple[int, int]) -> bool:
    """Determine if a move is safe from collisions with walls, self, or opponent."""
    snake = state.snake1 if snake_id == 1 else state.snake2
    opponent = state.snake2 if snake_id == 1 else state.snake1
    
    if not (0 <= next_pos[0] < state.grid_width and 0 <= next_pos[1] < state.grid_height):
        return False
        
    if next_pos in snake[:-1] or next_pos in opponent:
        return False
        
    opp_head = opponent[0]
    return not any(
        predict_next_position(opp_head, direction) == next_pos
        for direction in Direction
    )

class AggressiveAnticipationStrategy(SnakeStrategy):
    """An aggressive strategy that actively challenges for food position."""
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        """Calculate optimal move prioritizing food acquisition."""
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        opp_x, opp_y = opponent[0]
        food_x, food_y = state.food_position
        
        my_food_dist = abs(head_x - food_x) + abs(head_y - food_y)
        opp_food_dist = abs(opp_x - food_x) + abs(opp_y - food_y)
        
        if my_food_dist <= opp_food_dist:
            target_x, target_y = food_x, food_y
        else:
            dx = food_x - opp_x
            dy = food_y - opp_y
            target_x = max(0, min(int(opp_x + dx * 0.7), state.grid_width - 1))
            target_y = max(0, min(int(opp_y + dy * 0.7), state.grid_height - 1))
        
        moves: Dict[Direction, float] = {}
        for direction in Direction:
            new_pos = predict_next_position((head_x, head_y), direction)
            
            if not is_safe_move(state, snake_id, new_pos):
                continue
                
            dist_to_target = abs(target_x - new_pos[0]) + abs(target_y - new_pos[1])
            score = 1000 - dist_to_target
            
            moves[direction] = score
        
        if moves:
            return max(moves.items(), key=lambda x: x[1])[0]
        return random.choice(list(Direction))

class SafeFoodSeekingStrategy(SnakeStrategy):
    """A balanced strategy that considers both food and safety."""
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        """Determine next move with dynamic safety considerations."""
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        opp_head_x, opp_head_y = opponent[0]
        
        dist_to_opponent = abs(head_x - opp_head_x) + abs(head_y - opp_head_y)
        DANGER_THRESHOLD = 4
        
        moves: Dict[Direction, float] = {}
        for direction in Direction:
            new_pos = predict_next_position((head_x, head_y), direction)
            
            if not is_safe_move(state, snake_id, new_pos):
                continue
                
            dist_to_food = abs(food_x - new_pos[0]) + abs(food_y - new_pos[1])
            score = 1000 - dist_to_food
            
            if dist_to_opponent <= DANGER_THRESHOLD:
                min_opponent_dist = min(
                    abs(new_pos[0] - x) + abs(new_pos[1] - y)
                    for x, y in opponent
                )
                score += min_opponent_dist * 20
            
            moves[direction] = score
        
        if moves:
            return max(moves.items(), key=lambda x: x[1])[0]
        return random.choice(list(Direction))

class AdaptiveFoodSeekingStrategy(SnakeStrategy):
    """A strategy that repositions when food is unreachable."""
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        """Calculate optimal move with repositioning when food is unreachable."""
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        opp_x, opp_y = opponent[0]
        
        # Calculate distances and position advantage
        my_food_dist = abs(head_x - food_x) + abs(head_y - food_y)
        opp_food_dist = abs(opp_x - food_x) + abs(opp_y - food_y)
        dist_to_opponent = abs(head_x - opp_x) + abs(head_y - opp_y)
        
        # Determine if opponent is certain to reach food first
        LOSING_MARGIN = 3  # How much further we need to be to consider it "unreachable"
        food_unreachable = my_food_dist > opp_food_dist + LOSING_MARGIN
        
        # Set target position based on situation
        if food_unreachable:
            # Calculate opposite side of grid relative to opponent
            opposite_x = state.grid_width - 1 - opp_x
            opposite_y = state.grid_height - 1 - opp_y
            # Target halfway between opposite corner and food's future position
            target_x = (opposite_x + food_x) // 2
            target_y = (opposite_y + food_y) // 2
        else:
            target_x, target_y = food_x, food_y
        
        moves: Dict[Direction, float] = {}
        for direction in Direction:
            new_pos = predict_next_position((head_x, head_y), direction)
            
            if not is_safe_move(state, snake_id, new_pos):
                continue
            
            # Calculate base score from target distance
            dist_to_target = abs(target_x - new_pos[0]) + abs(target_y - new_pos[1])
            score = 1000 - dist_to_target
            
            # Add safety consideration when close to opponent
            if dist_to_opponent <= 4:
                min_opponent_dist = min(
                    abs(new_pos[0] - x) + abs(new_pos[1] - y)
                    for x, y in opponent
                )
                score += min_opponent_dist * 20
            
            # Add bonus for moves towards center when repositioning
            if food_unreachable:
                center_dist = abs(new_pos[0] - state.grid_width//2) + abs(new_pos[1] - state.grid_height//2)
                score += (state.grid_width + state.grid_height - center_dist) * 5
            
            moves[direction] = score
        
        if moves:
            return max(moves.items(), key=lambda x: x[1])[0]
        return random.choice(list(Direction))

class AggressiveAdaptiveStrategy(SnakeStrategy):
    """A strategy that aggressively pursues food but adapts position when disadvantaged."""
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        """Calculate optimal move with aggressive positioning."""
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        opp_x, opp_y = opponent[0]
        
        # Calculate distances
        my_food_dist = abs(head_x - food_x) + abs(head_y - food_y)
        opp_food_dist = abs(opp_x - food_x) + abs(opp_y - food_y)
        dist_to_opponent = abs(head_x - opp_x) + abs(head_y - opp_y)
        
        # More aggressive losing margin
        LOSING_MARGIN = 2  # Reduced from 3 to be more opportunistic
        food_unreachable = my_food_dist > opp_food_dist + LOSING_MARGIN
        
        if food_unreachable:
            # Calculate position on opposite side but closer to center
            target_x = state.grid_width - 1 - opp_x
            target_y = state.grid_height - 1 - opp_y
            
            # Bias towards the quadrant where food is
            if food_x > state.grid_width // 2:
                target_x = max(target_x, state.grid_width // 2)
            else:
                target_x = min(target_x, state.grid_width // 2)
                
            if food_y > state.grid_height // 2:
                target_y = max(target_y, state.grid_height // 2)
            else:
                target_y = min(target_y, state.grid_height // 2)
        else:
            # If close enough to food, go straight for it
            if my_food_dist <= opp_food_dist + 1:  # More aggressive food pursuit
                target_x, target_y = food_x, food_y
            else:
                # Try to intercept opponent's path
                dx = food_x - opp_x
                dy = food_y - opp_y
                target_x = max(0, min(int(opp_x + dx * 0.6), state.grid_width - 1))
                target_y = max(0, min(int(opp_y + dy * 0.6), state.grid_height - 1))
        
        moves: Dict[Direction, float] = {}
        for direction in Direction:
            new_pos = predict_next_position((head_x, head_y), direction)
            
            if not is_safe_move(state, snake_id, new_pos):
                continue
            
            # Calculate base score from target distance
            dist_to_target = abs(target_x - new_pos[0]) + abs(target_y - new_pos[1])
            score = 1000 - dist_to_target
            
            # Only consider safety when very close to opponent
            if dist_to_opponent <= 2:  # Reduced from 4 to be more aggressive
                min_opponent_dist = min(
                    abs(new_pos[0] - x) + abs(new_pos[1] - y)
                    for x, y in opponent
                )
                score += min_opponent_dist * 15  # Reduced from 20 to be more aggressive
            
            # Add bonus for moves towards the center when repositioning
            if food_unreachable:
                # Calculate center bias based on predicted next food location
                center_x = (state.grid_width // 2 + food_x) // 2
                center_y = (state.grid_height // 2 + food_y) // 2
                center_dist = abs(new_pos[0] - center_x) + abs(new_pos[1] - center_y)
                score += (state.grid_width + state.grid_height - center_dist) * 3
            
            moves[direction] = score
        
        if moves:
            return max(moves.items(), key=lambda x: x[1])[0]
        return random.choice(list(Direction))

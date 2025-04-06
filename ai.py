from __future__ import annotations
import random
import math
from typing import List, Tuple, Dict, Optional
from collections import deque

from enums import Direction
from game_state import GameState
from base import SnakeStrategy

class MovementHistory:
    """Tracks recent movements to prevent oscillations."""
    def __init__(self, size: int = 4):
        self.history = deque(maxlen=size)
        
    def add_move(self, direction: Direction):
        self.history.append(direction)
        
    def would_oscillate(self, next_direction: Direction) -> bool:
        """Check if adding this move would create an oscillation pattern."""
        if len(self.history) < 3:
            return False
            
        # Check for immediate reversal
        if self.history and Direction.opposite(self.history[-1]) == next_direction:
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

def predict_next_position(pos: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
    """Calculate next grid position given current position and movement direction."""
    return (pos[0] + direction.value[0], pos[1] + direction.value[1])

def get_safe_moves(state: GameState, snake_id: int, movement_history: MovementHistory) -> Dict[Direction, float]:
    """Get all legal moves with their base safety scores."""
    snake = state.snake1 if snake_id == 1 else state.snake2
    opponent = state.snake2 if snake_id == 1 else state.snake1
    head_x, head_y = snake[0]
    
    safe_moves: Dict[Direction, float] = {}
    
    for direction in Direction:
        if movement_history.would_oscillate(direction):
            continue
            
        new_pos = predict_next_position((head_x, head_y), direction)
        
        # Check boundaries
        if not (0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height):
            continue
            
        # Check collisions with snake bodies
        if new_pos in snake[:-1] or new_pos in opponent:
            continue
            
        # Check potential head-on collisions
        opp_head = opponent[0]
        if any(predict_next_position(opp_head, d) == new_pos for d in Direction):
            continue
            
        # Base safety score
        safe_moves[direction] = 100.0
    
    return safe_moves

class AggressiveAnticipationStrategy(SnakeStrategy):
    """An aggressive strategy that actively challenges for food position."""
    
    def __init__(self):
        self.movement_history = MovementHistory()
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        opp_x, opp_y = opponent[0]
        food_x, food_y = state.food_position
        
        # Get safe moves considering oscillation prevention
        moves = get_safe_moves(state, snake_id, self.movement_history)
        
        if not moves:
            # If no safe moves, try any legal direction
            for direction in Direction:
                new_pos = predict_next_position((head_x, head_y), direction)
                if 0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height:
                    self.movement_history.add_move(direction)
                    return direction
            return random.choice(list(Direction))
        
        # Score moves based on strategy
        my_food_dist = abs(head_x - food_x) + abs(head_y - food_y)
        opp_food_dist = abs(opp_x - food_x) + abs(opp_y - food_y)
        
        for direction in moves:
            new_pos = predict_next_position((head_x, head_y), direction)
            new_dist = abs(new_pos[0] - food_x) + abs(new_pos[1] - food_y)
            
            # Base score from food distance
            moves[direction] = 1000 - new_dist * 10
            
            # Extra points for reducing distance to food
            if new_dist < my_food_dist:
                moves[direction] += 50
            
            # Points for intercepting opponent's path
            if my_food_dist <= opp_food_dist:
                moves[direction] += 100
        
        best_move = max(moves.items(), key=lambda x: x[1])[0]
        self.movement_history.add_move(best_move)
        return best_move

class SafeFoodSeekingStrategy(SnakeStrategy):
    """A balanced strategy that considers both food and safety."""
    
    def __init__(self):
        self.movement_history = MovementHistory()
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        opp_x, opp_y = opponent[0]
        
        moves = get_safe_moves(state, snake_id, self.movement_history)
        
        if not moves:
            for direction in Direction:
                new_pos = predict_next_position((head_x, head_y), direction)
                if 0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height:
                    self.movement_history.add_move(direction)
                    return direction
            return random.choice(list(Direction))
        
        for direction in moves:
            new_pos = predict_next_position((head_x, head_y), direction)
            dist_to_food = abs(new_pos[0] - food_x) + abs(new_pos[1] - food_y)
            dist_to_opp = abs(new_pos[0] - opp_x) + abs(new_pos[1] - opp_y)
            
            # Balance between food pursuit and safety
            moves[direction] = 1000 - dist_to_food * 5
            
            # Safety bonus for maintaining distance from opponent
            if dist_to_opp < 3:
                moves[direction] -= 200
            else:
                moves[direction] += min(dist_to_opp * 10, 100)
        
        best_move = max(moves.items(), key=lambda x: x[1])[0]
        self.movement_history.add_move(best_move)
        return best_move

class AdaptiveFoodSeekingStrategy(SnakeStrategy):
    """A strategy that repositions when food is unreachable."""
    
    def __init__(self):
        self.movement_history = MovementHistory()
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        opp_x, opp_y = opponent[0]
        
        moves = get_safe_moves(state, snake_id, self.movement_history)
        
        if not moves:
            for direction in Direction:
                new_pos = predict_next_position((head_x, head_y), direction)
                if 0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height:
                    self.movement_history.add_move(direction)
                    return direction
            return random.choice(list(Direction))
        
        my_food_dist = abs(head_x - food_x) + abs(head_y - food_y)
        opp_food_dist = abs(opp_x - food_x) + abs(opp_y - food_y)
        food_unreachable = my_food_dist > opp_food_dist + 3
        
        for direction in moves:
            new_pos = predict_next_position((head_x, head_y), direction)
            
            if food_unreachable:
                # Move to opposite side of opponent
                target_x = state.grid_width - 1 - opp_x
                target_y = state.grid_height - 1 - opp_y
                dist_to_target = abs(new_pos[0] - target_x) + abs(new_pos[1] - target_y)
                moves[direction] = 1000 - dist_to_target * 5
                
                # Bonus for staying near center
                center_dist = abs(new_pos[0] - state.grid_width//2) + abs(new_pos[1] - state.grid_height//2)
                moves[direction] += (state.grid_width + state.grid_height - center_dist) * 2
            else:
                # Normal food seeking behavior
                dist_to_food = abs(new_pos[0] - food_x) + abs(new_pos[1] - food_y)
                moves[direction] = 1000 - dist_to_food * 10
                
                if dist_to_food < my_food_dist:
                    moves[direction] += 50
        
        best_move = max(moves.items(), key=lambda x: x[1])[0]
        self.movement_history.add_move(best_move)
        return best_move

class AggressiveAdaptiveStrategy(SnakeStrategy):
    """A strategy that aggressively pursues food but adapts position when disadvantaged."""
    
    def __init__(self):
        self.movement_history = MovementHistory()
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        opp_x, opp_y = opponent[0]
        
        moves = get_safe_moves(state, snake_id, self.movement_history)
        
        if not moves:
            for direction in Direction:
                new_pos = predict_next_position((head_x, head_y), direction)
                if 0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height:
                    self.movement_history.add_move(direction)
                    return direction
            return random.choice(list(Direction))
        
        my_food_dist = abs(head_x - food_x) + abs(head_y - food_y)
        opp_food_dist = abs(opp_x - food_x) + abs(opp_y - food_y)
        
        for direction in moves:
            new_pos = predict_next_position((head_x, head_y), direction)
            
            if my_food_dist <= opp_food_dist + 1:  # Aggressive mode
                dist_to_food = abs(new_pos[0] - food_x) + abs(new_pos[1] - food_y)
                moves[direction] = 1000 - dist_to_food * 15
                
                # Bonus for moves that block opponent
                if dist_to_food < opp_food_dist:
                    moves[direction] += 200
            else:  # Repositioning mode
                # Target point between center and food
                target_x = (state.grid_width//2 + food_x) // 2
                target_y = (state.grid_height//2 + food_y) // 2
                dist_to_target = abs(new_pos[0] - target_x) + abs(new_pos[1] - target_y)
                moves[direction] = 1000 - dist_to_target * 5
        
        best_move = max(moves.items(), key=lambda x: x[1])[0]
        self.movement_history.add_move(best_move)
        return best_move

class AggressiveAdaptiveRandomStrategy(AggressiveAdaptiveStrategy):
    """
    An aggressive adaptive strategy with a small chance of random movement.
    """

    def __init__(self, random_move_probability: float = 0.025):
        super().__init__()
        self.random_move_probability = random_move_probability

    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        """
        Determine the next move, with a chance of random movement.
        """
        if random.random() < self.random_move_probability:
            # Perform a random move
            snake = state.snake1 if snake_id == 1 else state.snake2
            head_x, head_y = snake[0]
            moves = get_safe_moves(state, snake_id, self.movement_history)

            if not moves:
                for direction in Direction:
                    new_pos = predict_next_position((head_x, head_y), direction)
                    if 0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height:
                        self.movement_history.add_move(direction)
                        return direction
                return random.choice(list(Direction))

            return random.choice(list(moves.keys()))

        # Otherwise, use the base AggressiveAdaptiveStrategy logic
        return super().get_next_move(state, snake_id)



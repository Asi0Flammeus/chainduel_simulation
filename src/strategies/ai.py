from __future__ import annotations
import random
import math
from typing import List, Tuple, Dict, Optional
from collections import deque

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

class AggressiveAnticipationStrategy(SnakeStrategy):
    """An aggressive strategy that actively challenges for food position."""
    
    def __init__(self):
        self.movement_history = MovementHistory()
    
    def get_safe_moves(self, state: GameState, snake_id: int) -> Dict[Direction, float]:
        """Get all legal moves with their base safety scores."""
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        safe_moves: Dict[Direction, float] = {}
        
        for direction in Direction:
            if self.movement_history.would_oscillate(direction):
                continue
                
            new_pos = (head_x + direction.value[0], head_y + direction.value[1])
            
            # Check boundaries
            if not (0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height):
                continue
                
            # Check collisions with snake bodies
            if new_pos in snake[:-1] or new_pos in opponent:
                continue
                
            # Check potential head-on collisions
            opp_head = opponent[0]
            if any((opp_head[0] + d.value[0], opp_head[1] + d.value[1]) == new_pos for d in Direction):
                continue
                
            # Base safety score
            safe_moves[direction] = 100.0
        
        return safe_moves
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        opp_x, opp_y = opponent[0]
        food_x, food_y = state.food_position
        
        moves = self.get_safe_moves(state, snake_id)
        
        if not moves:
            # If no safe moves, try any legal direction
            for direction in Direction:
                new_pos = (head_x + direction.value[0], head_y + direction.value[1])
                if 0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height:
                    self.movement_history.add_move(direction)
                    return direction
            return random.choice(list(Direction))
        
        my_food_dist = abs(head_x - food_x) + abs(head_y - food_y)
        opp_food_dist = abs(opp_x - food_x) + abs(opp_y - food_y)
        
        for direction in moves:
            new_pos = (head_x + direction.value[0], head_y + direction.value[1])
            new_dist = abs(new_pos[0] - food_x) + abs(new_pos[1] - food_y)
            
            moves[direction] = 1000 - new_dist * 10
            
            if new_dist < my_food_dist:
                moves[direction] += 50
            
            if my_food_dist <= opp_food_dist:
                moves[direction] += 100
        
        best_move = max(moves.items(), key=lambda x: x[1])[0]
        self.movement_history.add_move(best_move)
        return best_move

class NoisyAdaptiveAggressiveStrategy(SnakeStrategy):
    """An aggressive strategy that adapts to the situation with random noise for unpredictability."""
    
    def __init__(self):
        self.movement_history = MovementHistory()
        self.aggression_level = 0.7
        self.noise_factor = 0.05
        self.momentum_factor = 0.3
    
    def get_safe_moves(self, state: GameState, snake_id: int) -> Dict[Direction, float]:
        """Get all legal moves with their base safety scores."""
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        safe_moves: Dict[Direction, float] = {}
        
        for direction in Direction:
            if self.movement_history.would_oscillate(direction):
                continue
                
            new_pos = (head_x + direction.value[0], head_y + direction.value[1])
            
            # Check boundaries
            if not (0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height):
                continue
                
            # Check collisions with snake bodies
            if new_pos in snake[:-1] or new_pos in opponent:
                continue
                
            # Check potential head-on collisions
            opp_head = opponent[0]
            if any((opp_head[0] + d.value[0], opp_head[1] + d.value[1]) == new_pos for d in Direction):
                continue
                
            # Base safety score with noise
            safe_moves[direction] = 100.0 + random.uniform(-5, 5)
        
        return safe_moves
        
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        opp_x, opp_y = opponent[0]
        
        # Get safe moves
        moves = self.get_safe_moves(state, snake_id)
        
        if not moves:
            # If no safe moves, try any legal direction
            for direction in Direction:
                new_pos = (head_x + direction.value[0], head_y + direction.value[1])
                if 0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height:
                    self.movement_history.add_move(direction)
                    return direction
            return random.choice(list(Direction))
        
        # Calculate distances
        my_food_dist = abs(head_x - food_x) + abs(head_y - food_y)
        opp_food_dist = abs(opp_x - food_x) + abs(opp_y - food_y)
        
        # Adjust aggression based on game state
        score_diff = (state.score1 if snake_id == 1 else state.score2) - (state.score2 if snake_id == 1 else state.score1)
        self.aggression_level = 0.7 + (score_diff / 50000) * 0.3
        self.aggression_level = max(0.3, min(0.9, self.aggression_level))
        
        # Add random noise
        random_state = random.uniform(-1, 1) * self.noise_factor
        
        for direction in moves:
            new_pos = (head_x + direction.value[0], head_y + direction.value[1])
            dist_to_food = abs(new_pos[0] - food_x) + abs(new_pos[1] - food_y)
            dist_to_center = abs(new_pos[0] - state.grid_width//2) + abs(new_pos[1] - state.grid_height//2)
            dist_to_opp = abs(new_pos[0] - opp_x) + abs(new_pos[1] - opp_y)
            
            # Base score
            moves[direction] = 1000 - dist_to_food * (10 + random.uniform(-1, 1) * 2)
            
            # Aggressive or strategic positioning
            if my_food_dist <= opp_food_dist + 2:
                intercept_bonus = 200 * self.aggression_level
                if dist_to_food < my_food_dist:
                    moves[direction] += intercept_bonus * (1 + random_state)
                
                if dist_to_opp < 4:
                    block_bonus = 150 * self.aggression_level
                    moves[direction] += block_bonus * (1 + random.uniform(-0.2, 0.2))
            else:
                target_x = int(state.grid_width//2 * 0.7 + food_x * 0.3)
                target_y = int(state.grid_height//2 * 0.7 + food_y * 0.3)
                dist_to_target = abs(new_pos[0] - target_x) + abs(new_pos[1] - target_y)
                strategic_score = (1000 - dist_to_target * 5) * (1 - self.aggression_level)
                moves[direction] += strategic_score * (1 + random_state)
            
            # Momentum bonus
            last_move = self.movement_history.get_last_move()
            if last_move and direction == last_move:
                moves[direction] += 50 * self.momentum_factor * (1 + random.uniform(-0.1, 0.1))
            
            # Safety adjustments
            if dist_to_opp < 3:
                safety_penalty = 100 * (1 - self.aggression_level)
                moves[direction] -= safety_penalty * (1 + random.uniform(-0.1, 0.1))
            
            # Add noise
            moves[direction] += random.uniform(-20, 20) * self.noise_factor
        
        # Select best move
        best_move = max(moves.items(), key=lambda x: x[1])[0]
        self.movement_history.add_move(best_move)
        return best_move

class SafeFoodSeekingStrategy(SnakeStrategy):
    """A balanced strategy that considers both food and safety."""
    
    def __init__(self):
        self.movement_history = MovementHistory()
    
    def get_safe_moves(self, state: GameState, snake_id: int) -> Dict[Direction, float]:
        """Get all legal moves with their base safety scores."""
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        safe_moves: Dict[Direction, float] = {}
        
        for direction in Direction:
            if self.movement_history.would_oscillate(direction):
                continue
                
            new_pos = (head_x + direction.value[0], head_y + direction.value[1])
            
            # Check boundaries
            if not (0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height):
                continue
                
            # Check collisions with snake bodies
            if new_pos in snake[:-1] or new_pos in opponent:
                continue
                
            # Check potential head-on collisions
            opp_head = opponent[0]
            if any((opp_head[0] + d.value[0], opp_head[1] + d.value[1]) == new_pos for d in Direction):
                continue
                
            # Base safety score
            safe_moves[direction] = 100.0
        
        return safe_moves
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        opp_x, opp_y = opponent[0]
        
        moves = self.get_safe_moves(state, snake_id)
        
        if not moves:
            for direction in Direction:
                new_pos = (head_x + direction.value[0], head_y + direction.value[1])
                if 0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height:
                    self.movement_history.add_move(direction)
                    return direction
            return random.choice(list(Direction))
        
        for direction in moves:
            new_pos = (head_x + direction.value[0], head_y + direction.value[1])
            dist_to_food = abs(new_pos[0] - food_x) + abs(new_pos[1] - food_y)
            dist_to_opp = abs(new_pos[0] - opp_x) + abs(new_pos[1] - opp_y)
            
            moves[direction] = 1000 - dist_to_food * 5
            
            if dist_to_opp < 3:
                moves[direction] -= 200
            else:
                moves[direction] += min(dist_to_opp * 10, 100)
        
        best_move = max(moves.items(), key=lambda x: x[1])[0]
        self.movement_history.add_move(best_move)
        return best_move

class PathFinder:
    @staticmethod
    def find_path(start: Tuple[int, int], goal: Tuple[int, int], 
                  blocked: Set[Tuple[int, int]], grid_width: int, grid_height: int) -> List[Tuple[int, int]]:
        """A* pathfinding algorithm."""
        def heuristic(pos: Tuple[int, int]) -> float:
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
        def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_pos = (pos[0] + dx, pos[1] + dy)
                if (0 <= new_pos[0] < grid_width and 
                    0 <= new_pos[1] < grid_height and 
                    new_pos not in blocked):
                    neighbors.append(new_pos)
            return neighbors
        
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = frontier.pop(0)[1]
            
            if current == goal:
                break
                
            for next_pos in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(next_pos)
                    frontier.append((priority, next_pos))
                    frontier.sort()
                    came_from[next_pos] = current
        
        if goal not in came_from:
            return []
            
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

class SuperiorAdaptiveStrategy(SnakeStrategy):
    """Advanced strategy using pathfinding, territory control, and dynamic adaptation."""
    
    def __init__(self):
        self.movement_history = MovementHistory()
        self.pathfinder = PathFinder()
        # Strategy parameters
        self.aggression_base = 0.6
        self.territory_weight = 0.3
        self.safety_weight = 0.4
        self.food_weight = 0.5
        self.noise_factor = 0.1
        
    def evaluate_territory(self, pos: Tuple[int, int], state: GameState, snake_id: int) -> float:
        """Evaluate territory control value of a position."""
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = pos
        center_x, center_y = state.grid_width // 2, state.grid_height // 2
        
        # Calculate territory control score
        territory_score = 0
        
        # Center control value
        dist_to_center = abs(head_x - center_x) + abs(head_y - center_y)
        territory_score += (state.grid_width + state.grid_height - dist_to_center) * 2
        
        # Quadrant control
        my_quadrant = (head_x > center_x, head_y > center_y)
        opp_head = opponent[0]
        opp_quadrant = (opp_head[0] > center_x, opp_head[1] > center_y)
        if my_quadrant != opp_quadrant:
            territory_score += 100
        
        # Space control
        free_spaces = 0
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                check_x, check_y = head_x + dx, head_y + dy
                if (0 <= check_x < state.grid_width and 
                    0 <= check_y < state.grid_height and 
                    (check_x, check_y) not in snake and 
                    (check_x, check_y) not in opponent):
                    free_spaces += 1
        territory_score += free_spaces * 10
        
        return territory_score
        
    def get_safe_moves(self, state: GameState, snake_id: int) -> Dict[Direction, float]:
        """Get all legal moves with comprehensive safety scores."""
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        safe_moves: Dict[Direction, float] = {}
        
        for direction in Direction:
            if self.movement_history.would_oscillate(direction):
                continue
                
            new_pos = (head_x + direction.value[0], head_y + direction.value[1])
            
            # Basic safety checks
            if not (0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height):
                continue
            if new_pos in snake[:-1] or new_pos in opponent:
                continue
            
            # Advanced safety checks
            opp_head = opponent[0]
            potential_opp_moves = set()
            for d in Direction:
                opp_new_pos = (opp_head[0] + d.value[0], opp_head[1] + d.value[1])
                if (0 <= opp_new_pos[0] < state.grid_width and 
                    0 <= opp_new_pos[1] < state.grid_height):
                    potential_opp_moves.add(opp_new_pos)
            
            # Avoid head-on collisions unless snake is longer
            if new_pos in potential_opp_moves and len(snake) <= len(opponent):
                continue
            
            # Base safety score with territory evaluation
            safe_moves[direction] = 100.0 + self.evaluate_territory(new_pos, state, snake_id)
        
        return safe_moves
    
    def get_next_move(self, state: GameState, snake_id: int) -> Direction:
        snake = state.snake1 if snake_id == 1 else state.snake2
        opponent = state.snake2 if snake_id == 1 else state.snake1
        head_x, head_y = snake[0]
        food_x, food_y = state.food_position
        
        # Get safe moves with territory evaluation
        moves = self.get_safe_moves(state, snake_id)
        
        if not moves:
            # Emergency fallback
            for direction in Direction:
                new_pos = (head_x + direction.value[0], head_y + direction.value[1])
                if 0 <= new_pos[0] < state.grid_width and 0 <= new_pos[1] < state.grid_height:
                    return direction
            return random.choice(list(Direction))
        
        # Calculate strategic parameters
        score_diff = (state.score1 if snake_id == 1 else state.score2) - (state.score2 if snake_id == 1 else state.score1)
        length_diff = len(snake) - len(opponent)
        
        # Dynamic aggression adjustment
        aggression = self.aggression_base
        aggression += score_diff / 50000 * 0.3  # Score influence
        aggression += length_diff * 0.1  # Length influence
        aggression = max(0.2, min(0.9, aggression))
        
        # Find paths
        blocked = set(snake[:-1] + opponent)
        food_path = self.pathfinder.find_path(
            (head_x, head_y), 
            state.food_position,
            blocked,
            state.grid_width,
            state.grid_height
        )
        
        for direction in moves:
            new_pos = (head_x + direction.value[0], head_y + direction.value[1])
            
            # Base score from territory control
            moves[direction] += self.evaluate_territory(new_pos, state, snake_id) * self.territory_weight
            
            # Path-based scoring
            if food_path and len(food_path) > 1 and new_pos == food_path[1]:
                moves[direction] += 300 * self.food_weight
            
            # Strategic scoring
            opp_head = opponent[0]
            dist_to_opp = abs(new_pos[0] - opp_head[0]) + abs(new_pos[1] - opp_head[1])
            
            if dist_to_opp < 3:
                if len(snake) > len(opponent):
                    # Aggressive when longer
                    moves[direction] += 200 * aggression
                else:
                    # Defensive when shorter
                    moves[direction] -= 200 * (1 - aggression)
            
            # Add controlled randomness
            moves[direction] += random.uniform(-20, 20) * self.noise_factor
        
        # Select best move
        best_move = max(moves.items(), key=lambda x: x[1])[0]
        self.movement_history.add_move(best_move)
        return best_move

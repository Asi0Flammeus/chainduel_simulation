# src/utils/debug.py
import os
import time
from typing import List, Tuple
from datetime import datetime

class DebugLogger:
    def __init__(self, enable_debug: bool = False):
        self.debug_enabled = enable_debug
        self.log_file = None
        if enable_debug:
            os.makedirs('logs', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.log_file = open(f'logs/snake_debug_{timestamp}.txt', 'w')
    
    def log(self, message: str):
        """Log a general message with timestamp"""
        if not self.debug_enabled:
            return
        timestamp = time.strftime('%H:%M:%S')
        self.log_file.write(f"[{timestamp}] {message}\n")
        self.log_file.flush()

    def log_snake_state(self, snake_id: int, positions: List[Tuple[int, int]], direction: str):
        """Log snake position and direction"""
        if not self.debug_enabled:
            return
        timestamp = time.strftime('%H:%M:%S')
        self.log_file.write(f"\n[{timestamp}] Snake {snake_id} State:\n")
        self.log_file.write(f"  Direction: {direction}\n")
        self.log_file.write(f"  Positions: {positions}\n")
        self.log_file.flush()

    def log_key_press(self, key: str, current_direction: str):
        """Log key press events"""
        if not self.debug_enabled:
            return
        timestamp = time.strftime('%H:%M:%S')
        self.log_file.write(f"\n[{timestamp}] Key Press:\n")
        self.log_file.write(f"  Key: {key}\n")
        self.log_file.write(f"  Current Direction: {current_direction}\n")
        self.log_file.flush()

    def log_collision(self, collision_type: str, position: Tuple[int, int]):
        """Log collision events"""
        if not self.debug_enabled:
            return
        timestamp = time.strftime('%H:%M:%S')
        self.log_file.write(f"\n[{timestamp}] Collision:\n")
        self.log_file.write(f"  Type: {collision_type}\n")
        self.log_file.write(f"  Position: {position}\n")
        self.log_file.flush()

    def close(self):
        """Close the log file"""
        if self.debug_enabled and self.log_file:
            self.log_file.close()

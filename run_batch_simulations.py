#!/usr/bin/env python3
"""
Batch simulation runner for all AI strategies over multiple initial cases.
Generates a CSV of results and a Markdown summary of strategies and cases.
"""
import os
import sys
import random
import csv
from statistics import mean
from datetime import datetime

# Ensure src package is importable
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.common.constants import GameConfig
from src.common.enums import Direction
from src.core.game_state import GameState
from src.core.snake import Snake
from src.strategies.ai import (
    AggressiveAnticipationStrategy,
    NoisyAdaptiveAggressiveStrategy,
    SafeFoodSeekingStrategy,
    SuperiorAdaptiveStrategy,
)


def place_food_empty(snake1_body, snake2_body, cfg):
    """Place food at a random empty cell."""
    while True:
        x = random.randint(0, cfg.GRID_WIDTH - 1)
        y = random.randint(0, cfg.GRID_HEIGHT - 1)
        if (x, y) not in snake1_body and (x, y) not in snake2_body:
            return (x, y)


def simulate_one_game(case_cfg, strat1, strat2, cfg):
    """Simulate a single game for given case and strategies; return metrics."""
    # Unpack case configuration
    body1_init = [tuple(p) for p in case_cfg['snake1_body']]
    body2_init = [tuple(p) for p in case_cfg['snake2_body']]
    dir1_init = case_cfg['snake1_dir']
    dir2_init = case_cfg['snake2_dir']
    score1_init = case_cfg['score1']
    score2_init = case_cfg['score2']
    # Place initial food
    if case_cfg.get('random_food', False):
        food_init = place_food_empty(body1_init, body2_init, cfg)
    else:
        food_init = case_cfg['food_position']

    # Initialize game state and snakes
    state = GameState(
        snake1=list(body1_init),
        snake2=list(body2_init),
        food_position=food_init,
        grid_width=cfg.GRID_WIDTH,
        grid_height=cfg.GRID_HEIGHT,
        score1=score1_init,
        score2=score2_init,
    )
    snake1 = Snake(list(body1_init), dir1_init)
    snake2 = Snake(list(body2_init), dir2_init)
    history = []
    max_steps = 1000

    for step in range(max_steps):
        # Get moves
        d1 = strat1.get_next_move(state, 1)
        d2 = strat2.get_next_move(state, 2)
        snake1.set_direction(d1)
        snake2.set_direction(d2)

        # Move snakes, reset on wall collision
        if not snake1.move(cfg.GRID_WIDTH, cfg.GRID_HEIGHT):
            # reset to initial positions for this case
            snake1 = Snake(list(body1_init), dir1_init)
        if not snake2.move(cfg.GRID_WIDTH, cfg.GRID_HEIGHT):
            snake2 = Snake(list(body2_init), dir2_init)

        # Update state bodies
        state.snake1 = list(snake1.body)
        state.snake2 = list(snake2.body)

        # Collisions between snakes
        if snake1.check_collision(snake2):
            snake1 = Snake(list(body1_init), dir1_init)
            state.snake1 = list(snake1.body)
        if snake2.check_collision(snake1):
            snake2 = Snake(list(body2_init), dir2_init)
            state.snake2 = list(snake2.body)

        # Food collection and scoring
        # Snake1 eats
        if snake1.head == state.food_position:
            snake1.grow()
            pts = cfg.calculate_points(len(snake1.body))
            state.score1 += pts
            state.score2 -= pts
            if state.score1 >= cfg.WINNING_SCORE:
                history.append((state.score1, len(snake1.body), state.score2, len(snake2.body)))
                break
            state.food_position = place_food_empty(state.snake1, state.snake2, cfg)
        # Snake2 eats
        if snake2.head == state.food_position:
            snake2.grow()
            pts = cfg.calculate_points(len(snake2.body))
            state.score2 += pts
            state.score1 -= pts
            if state.score2 >= cfg.WINNING_SCORE:
                history.append((state.score1, len(snake1.body), state.score2, len(snake2.body)))
                break
            state.food_position = place_food_empty(state.snake1, state.snake2, cfg)

        # Record snapshot: (score1, len1, score2, len2)
        history.append((state.score1, len(snake1.body), state.score2, len(snake2.body)))

    # Final metrics
    final = history[-1] if history else (state.score1, len(snake1.body), state.score2, len(snake2.body))
    scores1 = [h[0] for h in history]
    scores2 = [h[2] for h in history]
    lengths1 = [h[1] for h in history]
    lengths2 = [h[3] for h in history]
    wins1 = 1 if final[0] > final[2] else 0
    wins2 = 1 - wins1
    return {
        'wins1': wins1,
        'wins2': wins2,
        'avg_score1': final[0],
        'avg_score2': final[2],
        'max_length1': max(lengths1) if lengths1 else len(body1_init),
        'max_length2': max(lengths2) if lengths2 else len(body2_init),
        'game_length': len(history),
    }


def main():
    cfg = GameConfig()
    # Prepare strategies
    strategies = [
        AggressiveAnticipationStrategy(),
        NoisyAdaptiveAggressiveStrategy(),
        SafeFoodSeekingStrategy(),
        SuperiorAdaptiveStrategy(),
    ]
    strat_names = [type(s).__name__ for s in strategies]

    # Define cases
    cx = cfg.GRID_WIDTH // 2
    cy = cfg.GRID_HEIGHT // 2
    base_len = cfg.INITIAL_SNAKE_LENGTH
    # Points for one food at L=base_len+1
    pts1 = cfg.calculate_points(base_len + 1)
    cases = [
        {
            'name': 'Classic Start',
            'snake1_body': [(2 - i, cy) for i in range(base_len)],
            'snake1_dir': Direction.RIGHT,
            'snake2_body': [(cfg.GRID_WIDTH - 3 + i, cy) for i in range(base_len)],
            'snake2_dir': Direction.LEFT,
            'score1': cfg.STARTING_SCORE,
            'score2': cfg.STARTING_SCORE,
            'food_position': (cx, cy),
            'random_food': False,
        },
        {
            'name': 'First Food Eaten; P2 at (26,13)',
            'snake1_body': [(cx - i, cy) for i in range(base_len + 1)],
            'snake1_dir': Direction.LEFT,
            'snake2_body': [(cx + 1, cy + 1), (cx + 2, cy + 1)],
            'snake2_dir': Direction.LEFT,
            'score1': cfg.STARTING_SCORE + pts1,
            'score2': cfg.STARTING_SCORE - pts1,
            'random_food': True,
        },
        {
            'name': 'First Food Eaten; P2 at (27,14)',
            'snake1_body': [(cx - i, cy) for i in range(base_len + 1)],
            'snake1_dir': Direction.LEFT,
            'snake2_body': [(cx + 2, cy + 2), (cx + 3, cy + 2)],
            'snake2_dir': Direction.LEFT,
            'score1': cfg.STARTING_SCORE + pts1,
            'score2': cfg.STARTING_SCORE - pts1,
            'random_food': True,
        },
        {
            'name': 'First Food Eaten; P2 at (27,12)',
            'snake1_body': [(cx - i, cy) for i in range(base_len + 1)],
            'snake1_dir': Direction.LEFT,
            'snake2_body': [(cx + 2, cy), (cx + 3, cy)],
            'snake2_dir': Direction.LEFT,
            'score1': cfg.STARTING_SCORE + pts1,
            'score2': cfg.STARTING_SCORE - pts1,
            'random_food': True,
        },
    ]

    # Prompt for runs
    while True:
        try:
            n = int(input('Enter number of simulation runs (10-10000): '))
            if 10 <= n <= 10000:
                break
            print('Please enter a number between 10 and 10000.')
        except ValueError:
            print('Invalid input; please enter an integer.')

    # Prepare output
    csv_file = os.path.join(ROOT, 'batch_results.csv')
    md_file = os.path.join(ROOT, 'STRATEGIES_AND_CASES.md')
    fieldnames = [
        'case', 'strategy1', 'strategy2', 'runs',
        'wins1', 'wins2', 'win_rate1', 'win_rate2',
        'avg_score1', 'avg_score2', 'max_length1', 'max_length2', 'avg_game_length'
    ]
    # Run simulations and write CSV
    with open(csv_file, 'w', newline='') as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        for case_cfg in cases:
            case_name = case_cfg['name']
            print(f"\n=== Case: {case_name} ===")
            for i, strat1 in enumerate(strategies):
                for j, strat2 in enumerate(strategies):
                    print(f"Running {strat_names[i]} vs {strat_names[j]} x{n}")
                    # Accumulate metrics
                    wins1 = wins2 = 0
                    scores1 = []
                    scores2 = []
                    lengths1 = []
                    lengths2 = []
                    games = []
                    for _ in range(n):
                        m = simulate_one_game(case_cfg, strat1, strat2, cfg)
                        wins1 += m['wins1']
                        wins2 += m['wins2']
                        scores1.append(m['avg_score1'])
                        scores2.append(m['avg_score2'])
                        lengths1.append(m['max_length1'])
                        lengths2.append(m['max_length2'])
                        games.append(m['game_length'])
                    # Write row
                    row = {
                        'case': case_name,
                        'strategy1': strat_names[i],
                        'strategy2': strat_names[j],
                        'runs': n,
                        'wins1': wins1,
                        'wins2': wins2,
                        'win_rate1': f"{wins1/n:.3f}",
                        'win_rate2': f"{wins2/n:.3f}",
                        'avg_score1': f"{mean(scores1):.1f}",
                        'avg_score2': f"{mean(scores2):.1f}",
                        'max_length1': max(lengths1),
                        'max_length2': max(lengths2),
                        'avg_game_length': f"{mean(games):.1f}",
                    }
                    writer.writerow(row)

    print(f"\nBatch results saved to {csv_file}")

    # Write Markdown summary
    with open(md_file, 'w') as mf:
        mf.write('# AI Strategies\n\n')
        for strat in strategies:
            name = type(strat).__name__
            desc = (strat.__doc__ or '').strip().replace('\n', ' ')
            mf.write(f"- **{name}**: {desc}\n")
        mf.write('\n# Initial Cases\n\n')
        mf.write('1. **Classic Start**: Both snakes start at opposite edges (length=2), first food at center.\n')
        mf.write('2. **First Food Eaten; P2 at (26,13)**: P1 has eaten first food, head at (25,12) length=3; P2 head at (26,13) length=2; next food spawned randomly.\n')
        mf.write('3. **First Food Eaten; P2 at (27,14)**: P1 as above; P2 head at (27,14) length=2; next food spawned randomly.\n')
        mf.write('4. **First Food Eaten; P2 at (27,12)**: P1 as above; P2 head at (27,12) length=2; next food spawned randomly.\n')
    print(f"Markdown summary saved to {md_file}")


if __name__ == '__main__':  # noqa: C901
    main()